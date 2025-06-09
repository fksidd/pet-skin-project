# app/api/support.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db_models import User, SupportInquiry, Notice
from app.database import get_db
from app.utils.auth import get_current_user, get_current_admin_user, utcnow
from app.schemas import APIResponse, NoticeResponse, InquiryCreate, AnswerUpdate, NoticeCreate
# APIRouter 생성 시 prefix를 제거합니다. main.py에서 설정하기 때문입니다.
router = APIRouter()


# --- 사용자 기능 ---
@router.post("/inquiry", response_model=APIResponse)
def create_inquiry(
    inquiry: InquiryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자가 새로운 문의를 등록합니다."""
    new_inquiry = SupportInquiry(user_id=current_user.id, content=inquiry.content, status="대기")
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    return APIResponse(success=True, message="문의가 성공적으로 등록되었습니다.", data={"inquiry_id": new_inquiry.id})

@router.post("/inquiry", response_model=APIResponse)
def create_inquiry(
    inquiry: InquiryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자가 새로운 문의를 등록합니다."""
    new_inquiry = SupportInquiry(
        user_id=current_user.id,
        content=inquiry.content,
        status="대기"
    )
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    return APIResponse(
        success=True,
        message="문의가 등록되었습니다.",
        data={"inquiry_id": new_inquiry.id}
    )

@router.get("/inquiries", response_model=APIResponse)
def get_user_inquiries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 본인의 문의 내역을 조회합니다."""
    inquiries = db.query(SupportInquiry).filter(
        SupportInquiry.user_id == current_user.id
    ).order_by(SupportInquiry.created_at.desc()).all()
    
    # ✅ 프론트엔드에서 필요한 모든 필드 포함
    data = [
        {
            "id": inq.id,
            "content": inq.content,
            "status": inq.status,
            "answer": inq.answer,
            "created_at": inq.created_at.isoformat() if inq.created_at else None,
            "answer_created_at": inq.answer_created_at.isoformat() if inq.answer_created_at else None
        }
        for inq in inquiries
    ]
    return APIResponse(
        success=True,
        message="문의 목록 조회 성공",
        data=data
    )

# --- 공통 기능 (사용자/관리자 모두 사용) ---
@router.get("/notices", response_model=APIResponse)
def get_notices(db: Session = Depends(get_db)):
    """전체 공지사항 목록을 조회합니다."""
    notices = db.query(Notice).order_by(Notice.created_at.desc()).all()
    data = [NoticeResponse.from_orm(n) for n in notices]
    return APIResponse(success=True, message="공지사항 목록 조회 성공", data=data)


# --- 관리자 전용 기능 (추가된 부분) ---
@router.put("/inquiries/{inquiry_id}/answer", response_model=APIResponse)
def answer_inquiry(
    inquiry_id: int,
    answer_data: AnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """관리자가 문의에 답변을 등록/수정합니다. (AdminInquiries.vue)"""
    inquiry = db.query(SupportInquiry).filter(SupportInquiry.id == inquiry_id).first()
    if not inquiry:
        return APIResponse(success=False, message="해당 문의를 찾을 수 없습니다.")
    
    inquiry.answer = answer_data.answer
    inquiry.status = "완료"
    inquiry.answer_created_at = utcnow()
    db.commit()
    return APIResponse(success=True, message="답변이 성공적으로 등록되었습니다.")

@router.post("/notices", response_model=APIResponse)
def create_notice(
    notice_data: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """관리자가 새 공지사항을 등록합니다. (AdminNotices.vue)"""
    new_notice = Notice(**notice_data.model_dump())
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return APIResponse(success=True, message="공지사항이 등록되었습니다.", data=NoticeResponse.from_orm(new_notice))

@router.put("/notices/{notice_id}", response_model=APIResponse)
def update_notice(
    notice_id: int,
    notice_data: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """관리자가 기존 공지사항을 수정합니다. (AdminNotices.vue)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        return APIResponse(success=False, message="해당 공지사항을 찾을 수 없습니다.")
        
    notice.title = notice_data.title
    notice.content = notice_data.content
    db.commit()
    db.refresh(notice)
    return APIResponse(success=True, message="공지사항이 수정되었습니다.", data=NoticeResponse.from_orm(notice))