# app/utils/auth.py

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.db_models import User

# 환경변수에서 보안 설정 읽기 (.env에서 설정, 코드에는 값 노출 금지)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
ADMIN_EMAILS = [email.strip() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()]

# OAuth2 토큰 스키마 (로그인 엔드포인트와 일치)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def utcnow():
    return datetime.now(timezone.utc)

def create_access_token(data: dict) -> str:
    """
    액세스 토큰(JWT) 생성
    """
    to_encode = data.copy()
    expire = utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """
    리프레시 토큰(JWT) 생성
    """
    to_encode = data.copy()
    expire = utcnow()+ timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str):
    """
    JWT 토큰 검증 (타입까지 확인)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None

def verify_access_token(token: str):
    """
    액세스 토큰만 검증 (payload 반환 또는 None)
    """
    return verify_token(token, "access")

def verify_refresh_token(token: str):
    """
    리프레시 토큰만 검증 (payload 반환 또는 None)
    """
    return verify_token(token, "refresh")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 사용자 인증 (액세스 토큰 기반)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token)
    if not payload:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception

    return user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    관리자 권한 체크
    """
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user
    