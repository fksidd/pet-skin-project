# app/api/pets.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.db_models import Pet, User
from app.utils.auth import get_current_user
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import shutil
import os
from datetime import datetime
from app.schemas import APIResponse, PetStatsResponse
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pets", response_model=APIResponse)
def get_pets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 반려동물 목록 조회"""
    pets = db.query(Pet).filter(Pet.user_id == current_user.id).all()
    pets_data = [
        {
            "id": pet.id,
            "name": pet.name,
            "breed": pet.breed or "품종 미상",
            "gender": pet.gender,
            "age": pet.age,
            "photo": pet.photo,
            "created_at": pet.created_at.isoformat() if pet.created_at else None
        }
        for pet in pets
    ]
    return APIResponse(
        success=True,
        message="반려동물 목록 조회 성공",
        data=pets_data
    )

@router.post("/pets", response_model=APIResponse)
def create_pet(
    name: str = Form(...),
    breed: str = Form(""),
    gender: str = Form("남"),
    age: int = Form(None),
    photo: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 반려동물 등록"""
    # 사진 업로드 처리
    photo_path = None
    if photo and photo.filename:
        upload_dir = "uploads/pets"
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(photo.filename)[1]
        filename = f"{current_user.id}_{timestamp}{file_extension}"
        photo_path = os.path.join(upload_dir, filename)
        try:
            with open(photo_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
        except Exception as e:
            return APIResponse(
                success=False,
                message=f"사진 업로드 실패: {str(e)}",
                data=None
            )

    # 반려동물 정보 저장
    new_pet = Pet(
        user_id=current_user.id,
        name=name.strip(),
        breed=breed.strip() if breed else None,
        gender=gender,
        age=age if age and age > 0 else None,
        photo=photo_path
    )

    try:
        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)
        return APIResponse(
            success=True,
            message=f"{name}이(가) 성공적으로 등록되었습니다.",
            data={
                "id": new_pet.id,
                "name": new_pet.name,
                "breed": new_pet.breed,
                "gender": new_pet.gender,
                "age": new_pet.age,
                "photo": new_pet.photo
            }
        )
    except Exception as e:
        db.rollback()
        return APIResponse(
            success=False,
            message=f"등록 실패: {str(e)}",
            data=None
        )

@router.get("/pets/{pet_id}", response_model=APIResponse)
def get_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 반려동물 정보 조회"""
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

    return APIResponse(
        success=True,
        message="반려동물 정보 조회 성공",
        data={
            "id": pet.id,
            "name": pet.name,
            "breed": pet.breed,
            "gender": pet.gender,
            "age": pet.age,
            "photo": pet.photo,
            "created_at": pet.created_at.isoformat() if pet.created_at else None
        }
    )

@router.put("/pets/{pet_id}", response_model=APIResponse)
def update_pet(
    pet_id: int,
    name: str = Form(None),
    breed: str = Form(None),
    gender: str = Form(None),
    age: int = Form(None),
    photo: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """반려동물 정보 수정"""
    # 1. 반려동물 존재 여부 확인
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

    # 2. 기존 사진 경로 백업
    old_photo_path = pet.photo
    new_photo_path = None

    try:
        # 3. 새 사진 업로드 처리
        if photo and photo.filename:
            upload_dir = "uploads/pets"
            os.makedirs(upload_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(photo.filename)[1]
            filename = f"{current_user.id}_{timestamp}{file_extension}"
            new_photo_path = os.path.join(upload_dir, filename)
            
            # 파일 저장
            with open(new_photo_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            
            # 기존 사진 경로 업데이트
            pet.photo = new_photo_path

        # 4. 정보 업데이트
        if name is not None: 
            pet.name = name.strip()
        if breed is not None:
            pet.breed = breed.strip() if breed else None
        if gender is not None:
            pet.gender = gender
        if age is not None:
            pet.age = age if age > 0 else None

        # 5. DB 커밋
        db.commit()
        db.refresh(pet)

        # 6. 기존 사진 삭제 (새 사진 업로드 성공 후)
        if new_photo_path and old_photo_path and os.path.exists(old_photo_path):
            os.remove(old_photo_path)

        return APIResponse(
            success=True,
            message=f"{pet.name}의 정보가 수정되었습니다",
            data={
                "id": pet.id,
                "name": pet.name,
                "breed": pet.breed,
                "gender": pet.gender,
                "age": pet.age,
                "photo": pet.photo
            }
        )

    except Exception as e:
        db.rollback()
        # 7. 업로드 실패 시 새로 업로드한 파일 삭제
        if new_photo_path and os.path.exists(new_photo_path):
            os.remove(new_photo_path)
        return APIResponse(
            success=False,
            message=f"수정 실패: {str(e)}",
            data=None
        )

@router.delete("/pets/{pet_id}", response_model=APIResponse)
def delete_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """반려동물 삭제"""
    # 1. 반려동물 존재 여부 확인
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

    # 2. 정보 백업
    pet_name = pet.name
    photo_path = pet.photo

    try:
        # 3. DB 삭제
        db.delete(pet)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DB 삭제 오류: {str(e)}")
        return APIResponse(
            success=False,
            message=f"삭제 실패: {str(e)}",
            data=None
        )

    # 4. 파일 삭제 (실패 시 로그만 기록)
    if photo_path and os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except Exception as e:
            logger.error(f"파일 삭제 실패: {photo_path}, 오류: {str(e)}")

    return APIResponse(
        success=True,
        message=f"{pet_name}이(가) 삭제되었습니다",
        data={"deleted_id": pet_id}
    )

@router.get("/pets/{pet_id}/stats", response_model=APIResponse)
def get_pet_stats(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
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

        # 통계 계산
        diagnosis_count = len(pet.diagnoses)
        latest_diagnosis = None
        if pet.diagnoses:
            latest = max(pet.diagnoses, key=lambda d: d.created_at)
            latest_diagnosis = {
                "diagnosis": latest.diagnosis,
                "date": latest.created_at.isoformat(),
                "confidence": latest.confidence
            }

        return APIResponse(
            success=True,
            message="반려동물 통계 정보 조회 성공",
            data=PetStatsResponse(
                pet_name=pet.name,
                total_diagnoses=diagnosis_count,
                latest_diagnosis=latest_diagnosis,
                registered_date=pet.created_at.isoformat() if pet.created_at else None
            ).dict()
        )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"통계 조회 실패: {str(e)}",
            data=None
        )