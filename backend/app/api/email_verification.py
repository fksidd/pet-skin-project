from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from app.database import get_db
from app.db_models import EmailVerification, User
from app.utils.email_service import fast_mail
from fastapi_mail import MessageSchema, MessageType
from app.schemas import EmailRequest, APIResponse, VerifyCodeRequest

router = APIRouter()

def generate_secure_code(length=6):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

@router.post("/send-code",response_model=APIResponse)
async def send_verification_code(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    email = request.email
    # 기존 사용자 확인
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "이미 가입된 이메일입니다")
    # 기존 인증 기록 삭제
    db.query(EmailVerification).filter(EmailVerification.email == email).delete()
    # 새 코드 생성
    code = generate_secure_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    new_code = EmailVerification(
        email=email,
        code=code,
        expires_at=expires_at
    )
    db.add(new_code)
    db.commit()
    # 이메일 전송
    html = f"<h3>인증번호: {code}</h3><p>5분 내 입력해주세요</p>"
    message = MessageSchema(
        subject="[PetSkin] 이메일 인증 요청",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    background_tasks.add_task(fast_mail.send_message, message)
    return {"success": True, "message": "인증코드가 전송되었습니다", "data": None}

@router.post("/verify-code", response_model=APIResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    record = db.query(EmailVerification).filter(
        EmailVerification.email == request.email, 
        EmailVerification.code == request.code,          
        EmailVerification.expires_at > datetime.utcnow()
    ).first()

    if not record:
        raise HTTPException(400, "잘못된 코드 또는 만료된 인증번호")

    record.is_verified = True
    db.commit()
    return {"success": True, "message": "이메일 인증 성공", "data": None}