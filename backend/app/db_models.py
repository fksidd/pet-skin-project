from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30))
    password = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    pets = relationship("Pet", back_populates="owner", cascade="all, delete")
    alerts = relationship("UserAlert", back_populates="user", uselist=False)
    inquiries = relationship("SupportInquiry", back_populates="user")
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")  

    favorite_hospitals = relationship("FavoriteHospital", back_populates="user", cascade="all, delete")
    hospital_reviews = relationship("HospitalReview", back_populates="user", cascade="all, delete")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False)  # JWT 리프레시 토큰 저장
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # 토큰 만료 시간
    revoked = Column(Boolean, default=False)  # 강제 무효화 여부
    
    user = relationship("User", back_populates="refresh_tokens")  # 사용자 관계 설정
class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    breed = Column(String(100))
    gender = Column(Enum("남", "여", name="gender_enum"), default="남")
    age = Column(Integer)
    photo = Column(String(255))
    created_at = Column(DateTime, default=utcnow)
    owner = relationship("User", back_populates="pets")
    diagnoses = relationship("DiagnosisHistory", back_populates="pet", cascade="all, delete")

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    diagnosis = Column(String(100), nullable=False)
    confidence = Column(Float)
    details = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    pet = relationship("Pet", back_populates="diagnoses")

class UserAlert(Base):
    __tablename__ = "user_alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diagnosis_alert = Column(Boolean, default=False)
    news_alert = Column(Boolean, default=False)
    user = relationship("User", back_populates="alerts")

class SupportInquiry(Base):
    __tablename__ = "support_inquiries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    status = Column(Enum("대기", "처리중", "완료"), default="대기")
    created_at = Column(DateTime, default=utcnow)
    user = relationship("User", back_populates="inquiries")
    answer = Column(Text, nullable=True)  
    answer_created_at = Column(DateTime, nullable=True)

class Notice(Base):
    __tablename__ = "notices"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)
    attempt_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="email_verifications")

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(30))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    is_24hour = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    favorites = relationship("FavoriteHospital", back_populates="hospital", cascade="all, delete")
    reviews = relationship("HospitalReview", back_populates="hospital", cascade="all, delete")

class FavoriteHospital(Base):
    __tablename__ = "favorite_hospitals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="favorite_hospitals")
    hospital = relationship("Hospital", back_populates="favorites")

class HospitalReview(Base):
    __tablename__ = "hospital_reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500))
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="hospital_reviews")
    hospital = relationship("Hospital", back_populates="reviews")