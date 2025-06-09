from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from app.schemas import APIResponse

# 프로젝트 모듈 임포트
from app.database import get_db
from app.db_models import DiagnosisHistory, Pet, User, UserAlert
from app.utils.auth import get_current_user
from app.api.notifications import EmailService

router = APIRouter(tags=["Diagnosis"], prefix="/diagnosis")
email_service = EmailService()

# ------------------- Pydantic 모델 정의 -------------------
class DiagnosisCreate(BaseModel):
    pet_id: int = Field(..., example=1)
    diagnosis: str = Field(..., example="피부염")
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.95)
    details: Optional[str] = Field(None, example="추가 설명")

    @validator("confidence")
    def confidence_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("신뢰도(confidence)는 0.0~1.0 사이여야 합니다.")
        return round(v, 2)

class DiagnosisResponse(BaseModel):
    id: int
    pet_name: str
    diagnosis: str
    confidence: float
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DiagnosisStatsResponse(BaseModel):
    pet_id: int
    period: str
    total_diagnoses: int
    diagnosis_distribution: Dict[str, int]
    average_confidence: float
    most_common_diagnosis: Optional[str]
    latest_diagnosis: Optional[str]

# ------------------- 진단 결과 저장 -------------------
@router.post("/save", response_model=DiagnosisResponse)
async def save_diagnosis(
    diag_data: DiagnosisCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 진단 결과 저장 (JSON 요청)
    """
    pet = db.query(Pet).filter(
        Pet.id == diag_data.pet_id,
        Pet.user_id == current_user.id
    ).first()
    if not pet:
        raise HTTPException(status_code=403, detail="반려동물 소유권이 없습니다")

    try:
        new_diag = DiagnosisHistory(
            pet_id=diag_data.pet_id,
            diagnosis=diag_data.diagnosis,
            confidence=diag_data.confidence,
            details=diag_data.details
        )
        db.add(new_diag)
        db.commit()
        db.refresh(new_diag)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"저장 실패: {str(e)}")

    # 알림 전송(비동기)
    alerts = db.query(UserAlert).filter(
        UserAlert.user_id == current_user.id,
        UserAlert.diagnosis_alert == False
    ).first()
    if alerts:
        background_tasks.add_task(
            send_diagnosis_email,
            current_user.email,
            pet.name,
            diag_data.diagnosis
        )

    return DiagnosisResponse(
        id=new_diag.id,
        pet_name=pet.name,
        diagnosis=new_diag.diagnosis,
        confidence=new_diag.confidence,
        details=new_diag.details,
        created_at=new_diag.created_at
    )

# ------------------- 진단 이력 조회 -------------------
@router.get("/history/{pet_id}", response_model=APIResponse)
def get_diagnosis_history(
    pet_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.user_id == current_user.id
    ).first()
    if not pet:
        return APIResponse(success=False, message="반려동물을 찾을 수 없습니다.", data=None)

    try:
        query = db.query(DiagnosisHistory).filter(
            DiagnosisHistory.pet_id == pet_id
        ).order_by(DiagnosisHistory.created_at.desc())

        total = query.count()
        diagnoses = query.offset((page-1)*limit).limit(limit).all()
        results = [
            {
                "id": d.id,
                "pet_name": pet.name,
                "diagnosis": d.diagnosis,
                "confidence": d.confidence,
                "details": d.details,
                "created_at": d.created_at
            }
            for d in diagnoses
        ]
        return APIResponse(
            success=True,
            message="진단 이력 조회 성공",
            data={
                "total": total,
                "page": page,
                "limit": limit,
                "results": results
            }
        )
    except Exception as e:
        return APIResponse(success=False, message=f"조회 실패: {str(e)}", data=None)

# ------------------- 진단 통계 조회 -------------------
@router.get("/stats/{pet_id}", response_model=APIResponse)
def get_diagnosis_stats(
    pet_id: int,
    period_days: int = Query(30, ge=1, le=365, description="통계 기간(일)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 반려동물 존재 여부 확인
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.user_id == current_user.id
    ).first()
    if not pet:
        return APIResponse(
            success=False,
            message="반려동물을 찾을 수 없습니다",
            data=None
        )

    try:
        start_date = datetime.now() - timedelta(days=period_days)
        recent_data = db.query(DiagnosisHistory).filter(
            DiagnosisHistory.pet_id == pet_id,
            DiagnosisHistory.created_at >= start_date
        ).all()

        # 통계 계산 로직
        diagnosis_counts = {}
        total_confidence = 0.0
        for d in recent_data:
            diagnosis_counts[d.diagnosis] = diagnosis_counts.get(d.diagnosis, 0) + 1
            total_confidence += d.confidence

        avg_confidence = round(total_confidence / len(recent_data), 2) if recent_data else 0.0
        latest_diagnosis = max(recent_data, key=lambda x: x.created_at).diagnosis if recent_data else None
        most_common = max(diagnosis_counts, key=diagnosis_counts.get, default=None)

        # APIResponse로 감싸서 반환
        return APIResponse(
            success=True,
            message="진단 통계 조회 성공",
            data=DiagnosisStatsResponse(
                pet_id=pet_id,
                period=f"최근 {period_days}일",
                total_diagnoses=len(recent_data),
                diagnosis_distribution=diagnosis_counts,
                average_confidence=avg_confidence,
                most_common_diagnosis=most_common,
                latest_diagnosis=latest_diagnosis
            )
        )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"통계 생성 실패: {str(e)}",
            data=None
        )

# ------------------- 진단 기록 삭제 -------------------
@router.delete("/{diagnosis_id}", response_model=APIResponse)
def delete_diagnosis(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diagnosis = db.query(DiagnosisHistory).join(Pet).filter(
        DiagnosisHistory.id == diagnosis_id,
        Pet.user_id == current_user.id
    ).first()
    
    if not diagnosis:
        return APIResponse(
            success=False,
            message="진단 기록을 찾을 수 없습니다",
            data=None
        )

    try:
        db.delete(diagnosis)
        db.commit()
        return APIResponse(
            success=True,
            message="진단 기록이 삭제되었습니다",
            data={"deleted_id": diagnosis_id}
        )
    except Exception as e:
        db.rollback()
        return APIResponse(
            success=False,
            message=f"삭제 실패: {str(e)}",
            data=None
        )

# ------------------- 공통 유틸리티 -------------------
async def send_diagnosis_email(email: str, pet_name: str, diagnosis: str):
    """진단 결과 알림 이메일 발송"""
    try:
        subject = f"[펫스프] {pet_name}의 진단 결과"
        body = f"""
        <h3>{pet_name}의 진단 결과가 나왔습니다</h3>
        <p>진단명: {diagnosis}</p>
        <p>앱에서 상세 결과를 확인해주세요.</p>
        """
        await email_service.send_diagnosis_alert(email, subject, body)
    except Exception as e:
        print(f"이메일 발송 실패: {e}")