# app/api/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.db_models import UserAlert, User
from app.utils.auth import get_current_user 
from app.schemas import APIResponse
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

# 환경변수 로드
load_dotenv()

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/alerts", response_model=APIResponse)
def get_user_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 알림 설정 조회"""
    alerts = db.query(UserAlert).filter(UserAlert.user_id == current_user.id).first()
    
    # 기본 설정 생성 로직
    if not alerts:
        alerts = UserAlert(
            user_id=current_user.id,
            diagnosis_alert=False,
            news_alert=False
        )
        db.add(alerts)
        db.commit()
        db.refresh(alerts)

    return APIResponse(
        success=True,
        message="알림 설정 조회 성공",
        data={
            "diagnosis_alert": alerts.diagnosis_alert,
            "news_alert": alerts.news_alert
        }
    )

@router.put("/alerts", response_model=APIResponse)
def update_user_alerts(
    diagnosis_alert: bool = None,
    news_alert: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 알림 설정 수정"""
    try:
        alerts = db.query(UserAlert).filter(UserAlert.user_id == current_user.id).first()
        
        # 최초 생성 시
        if not alerts:
            alerts = UserAlert(user_id=current_user.id)
            db.add(alerts)
        
        # 필드 업데이트
        if diagnosis_alert is not None:
            alerts.diagnosis_alert = diagnosis_alert
        if news_alert is not None:
            alerts.news_alert = news_alert
        
        db.commit()
        db.refresh(alerts)  # 갱신된 데이터 가져오기
        
        return APIResponse(
            success=True,
            message="알림 설정이 업데이트되었습니다.",
            data={
                "diagnosis_alert": alerts.diagnosis_alert,
                "news_alert": alerts.news_alert
            }
        )
        
    except Exception as e:
        db.rollback()
        return APIResponse(
            success=False,
            message=f"알림 설정 업데이트 실패: {str(e)}",
            data=None
        )

# 이메일 알림 서비스
class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")

        if not all([self.smtp_server, self.smtp_port, self.email, self.password]):
            raise RuntimeError("SMTP 환경변수 설정이 누락되었습니다.")

    def send_diagnosis_alert(self, user_email: str, pet_name: str, diagnosis: str):
        """진단 결과 알림 이메일 발송"""
        subject = f"[펫스프] {pet_name}의 진단 결과가 나왔습니다"
        body = f"""
        안녕하세요!

        {pet_name}의 피부 진단 결과가 나왔습니다.
        진단 결과: {diagnosis}

        자세한 내용은 펫스프 앱에서 확인하실 수 있습니다.

        감사합니다.
        펫스프 팀
        """
        return self._send_email(user_email, subject, body)

    def send_verification_code(self, user_email: str, code: str):
        """이메일 인증코드 발송"""
        subject = "[펫스프] 이메일 인증 코드"
        body = f"""
        안녕하세요! 펫스프 이메일 인증 코드입니다.

        인증코드: {code}
        유효시간: 5분

        감사합니다.
        """
        return self._send_email(user_email, subject, body)

    def _send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False
