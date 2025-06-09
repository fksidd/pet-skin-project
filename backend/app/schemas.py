from pydantic import BaseModel, ConfigDict
from typing import Any, Optional
from datetime import datetime

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: Optional[datetime]  
    
    model_config = ConfigDict(from_attributes=True)  

class PetStatsResponse(BaseModel):
    pet_name: str
    total_diagnoses: int
    latest_diagnosis: Optional[dict]
    registered_date: Optional[str]

class InquiryCreate(BaseModel):
    content: str

class NoticeCreate(BaseModel):
    title: str
    content: str

class AnswerUpdate(BaseModel):
    answer: str

class EmailRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str