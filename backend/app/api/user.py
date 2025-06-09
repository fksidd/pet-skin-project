from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.schemas import APIResponse
from app.db_models import EmailVerification
from app.database import get_db
from app.db_models import User, RefreshToken
from app.schemas import UserCreate, UserRead
from app.utils.auth import (
    create_access_token, 
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from app.utils.hashing import hash_password, verify_password

def utcnow():
    return datetime.now(timezone.utc)

router = APIRouter()

@router.post("/token", response_model=APIResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인 및 토큰 발급 (Access + Refresh)"""
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password):
        return APIResponse(
            success=False,
            message="이메일 또는 비밀번호가 일치하지 않습니다.",
            data=None
        )
    db.query(RefreshToken).filter(RefreshToken.user_id == db_user.id).delete()
    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})
    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=db_user.id,
        expires_at=utcnow() + timedelta(days=7)
    )
    db.add(db_refresh)
    db.commit()
    return APIResponse(
        success=True,
        message="로그인 성공",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )

@router.post("/refresh", response_model=APIResponse)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """리프레시 토큰으로 새 액세스 토큰 발급"""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        return APIResponse(
            success=False,
            message="유효하지 않은 리프레시 토큰",
            data=None
        )
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.expires_at > utcnow()
    ).first()
    if not db_token:
        return APIResponse(
            success=False,
            message="만료되었거나 존재하지 않는 토큰",
            data=None
        )
    new_access_token = create_access_token({"sub": payload.get("sub")})
    return APIResponse(
        success=True,
        message="새 액세스 토큰 발급 성공",
        data={"access_token": new_access_token}
    )

@router.post("/register/", response_model=APIResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    verified = db.query(EmailVerification).filter(
        EmailVerification.email == user.email,
        EmailVerification.is_verified == True,
        EmailVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not verified:
        return APIResponse(
            success=False,
            message="이메일 인증이 완료되지 않았습니다",
            data=None
        )

    # 기존 회원가입 로직 유지
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return APIResponse(
            success=False,
            message="이미 등록된 이메일입니다.",
            data=None
        )
    
    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return APIResponse(
        success=True,
        message="회원가입이 완료되었습니다.",
        data={...}
    )

@router.get("/me", response_model=APIResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return APIResponse(
        success=True,
        message="사용자 정보 조회 성공",
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "created_at": current_user.created_at
        }
    )

@router.delete("/delete-account", response_model=APIResponse)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """계정 삭제"""
    try:
        db.delete(current_user)
        db.commit()
        return APIResponse(
            success=True,
            message="계정이 삭제되었습니다.",
            data=None
        )
    except Exception as e:
        db.rollback()
        return APIResponse(
            success=False,
            message=f"계정 삭제 실패: {str(e)}",
            data=None
        )

@router.post("/change-password", response_model=APIResponse)
def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """비밀번호 변경"""
    if not verify_password(current_password, current_user.password):
        return APIResponse(
            success=False,
            message="현재 비밀번호가 일치하지 않습니다.",
            data=None
        )
    current_user.password = hash_password(new_password)
    db.commit()
    return APIResponse(
        success=True,
        message="비밀번호가 성공적으로 변경되었습니다.",
        data=None
    )