from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.db_models import Base
from app.api import user, predict

app = FastAPI()

# CORS 미들웨어 추가 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(user.router, prefix="/api")
app.include_router(predict.router)