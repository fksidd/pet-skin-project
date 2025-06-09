import os
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType 
from dotenv import load_dotenv
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_EMAIL"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("SMTP_EMAIL"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 465)),
    MAIL_SERVER=os.getenv("SMTP_SERVER"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
fast_mail = FastMail(conf)

async def send_email():
    message = MessageSchema(
        subject="테스트 이메일",
        recipients=["recipient@example.com"],
        body="<h1>HTML 내용</h1>",
        subtype=MessageType.html  # 올바른 Enum 사용
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)