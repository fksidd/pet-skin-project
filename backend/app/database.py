# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:admin@127.0.0.1:3306/petdb?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 추가된 부분
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()