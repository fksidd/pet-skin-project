from dotenv import load_dotenv
load_dotenv()  
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.db_models import Base
from app.api import user, predict, pets, diagnosis, notifications, support, admin, email_verification, hospitals
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import anyio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 초기화
    print("Server starting...")
    async with anyio.create_task_group() as tg:
        yield
    # 서버 종료 시 정리
    print("Server shutting down...")

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(
    email_verification.router,
    prefix="/api/email",
    tags=["email_verification"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/api", tags=["user"])
app.include_router(predict.router, prefix="/api", tags=["predict"]) 
app.include_router(pets.router, prefix="/api", tags=["pets"])
app.include_router(diagnosis.router, prefix="/api", tags=["diagnosis"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(hospitals.router, prefix="/api", tags=["hospitals"])
app.include_router(support.router, prefix="/api/support", tags=["support"]) 
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/example")
async def example():
    return jsonable_encoder({"date": datetime.now()})
