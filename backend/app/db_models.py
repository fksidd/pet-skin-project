from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base   
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    pets = relationship("Pet", back_populates="owner", cascade="all, delete")
    alerts = relationship("UserAlert", back_populates="user", uselist=False)
    inquiries = relationship("SupportInquiry", back_populates="user")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    breed = Column(String(100))
    gender = Column(Enum("남", "여"), default="남")
    age = Column(Integer)
    photo = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship("User", back_populates="pets")
    diagnoses = relationship("DiagnosisHistory", back_populates="pet", cascade="all, delete")

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    diagnosis = Column(String(100), nullable=False)
    confidence = Column(Float)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    pet = relationship("Pet", back_populates="diagnoses")

class UserAlert(Base):
    __tablename__ = "user_alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diagnosis_alert = Column(Boolean, default=True)
    news_alert = Column(Boolean, default=False)
    user = relationship("User", back_populates="alerts")

class SupportInquiry(Base):
    __tablename__ = "support_inquiries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    status = Column(Enum("대기", "처리중", "완료"), default="대기")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="inquiries")

class Notice(Base):
    __tablename__ = "notices"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)