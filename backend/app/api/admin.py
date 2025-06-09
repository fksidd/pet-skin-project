
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db
from app.db_models import User, SupportInquiry, Notice, EmailVerification, Pet, RefreshToken, FavoriteHospital, HospitalReview, UserAlert
from app.utils.auth import get_current_admin_user
from app.schemas import APIResponse, NoticeResponse


router = APIRouter()

# --- 관리자 대시보드 통계 ---
@router.get("/stats", response_model=APIResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """관리자 대시보드에 필요한 통계 정보를 한 번에 제공합니다. (AdminDashboardPage.vue 최적화)"""
    try:
        total_users = db.query(User).count()
        pending_inquiries = db.query(SupportInquiry).filter(SupportInquiry.status == "대기").count()
        total_notices = db.query(Notice).count()
        
        stats_data = {
            "totalUsers": total_users,
            "pendingInquiries": pending_inquiries,
            "totalNotices": total_notices
        }
        return APIResponse(success=True, message="관리자 통계 조회 성공", data=stats_data)
    except Exception as e:
        return APIResponse(success=False, message=f"통계 조회 실패: {str(e)}")


# --- 회원 관리 ---
@router.get("/users", response_model=APIResponse)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """전체 회원 목록을 조회합니다. (AdminUsers.vue)"""
    users = db.query(User).order_by(User.id.desc()).all()
    # AdminUsers.vue에서 role을 사용하므로, 스키마 대신 직접 직렬화합니다.
    users_data = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        } for user in users
    ]
    return APIResponse(success=True, message="전체 회원 조회 성공", data=users_data)


@router.delete("/users/{user_id}", response_model=APIResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        return APIResponse(success=False, message="해당 회원을 찾을 수 없습니다.")
    if user_to_delete.role == 'admin':
        return APIResponse(success=False, message="관리자 계정은 삭제할 수 없습니다.")
    try:
        # 관련 데이터 삭제
        db.query(EmailVerification).filter(EmailVerification.user_id == user_id).delete()
        db.query(Pet).filter(Pet.user_id == user_id).delete()
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.query(FavoriteHospital).filter(FavoriteHospital.user_id == user_id).delete()
        db.query(HospitalReview).filter(HospitalReview.user_id == user_id).delete()
        db.query(UserAlert).filter(UserAlert.user_id == user_id).delete()  # 추가
        db.delete(user_to_delete)
        db.commit()
        return APIResponse(success=True, message="회원이 성공적으로 삭제되었습니다.", data={"user_id": user_id})
    except Exception as e:
        db.rollback()
        return APIResponse(success=False, message=f"회원 삭제 실패: {str(e)}")


# --- 문의 관리 ---
@router.get("/inquiries", response_model=APIResponse)
def get_all_inquiries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """전체 문의 목록을 조회합니다. (AdminInquiries.vue)"""
    inquiries = db.query(SupportInquiry).order_by(SupportInquiry.created_at.desc()).all()
    # 프론트엔드에서 필요한 모든 필드를 포함하여 직렬화
    inquiries_data = [
        {
            "id": inq.id,
            "user_id": inq.user_id,
            "content": inq.content,
            "status": inq.status,
            "answer": inq.answer,
            "created_at": inq.created_at.isoformat() if inq.created_at else None,
            "answer_created_at": inq.answer_created_at.isoformat() if inq.answer_created_at else None
        } for inq in inquiries
    ]
    return APIResponse(success=True, message="전체 문의 조회 성공", data=inquiries_data)


@router.delete("/inquiries/{inquiry_id}", response_model=APIResponse)
def delete_inquiry_by_admin(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """특정 문의를 삭제합니다. (AdminInquiries.vue)"""
    inquiry = db.query(SupportInquiry).filter(SupportInquiry.id == inquiry_id).first()
    if not inquiry:
        return APIResponse(success=False, message="해당 문의를 찾을 수 없습니다.")
    
    try:
        db.delete(inquiry)
        db.commit()
        return APIResponse(success=True, message="문의가 성공적으로 삭제되었습니다.", data={"inquiry_id": inquiry_id})
    except Exception as e:
        db.rollback()
        return APIResponse(success=False, message=f"문의 삭제 실패: {str(e)}")


# --- 공지사항 관리 ---
@router.get("/notices", response_model=APIResponse)
def get_all_notices_by_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """전체 공지사항 목록을 조회합니다. (AdminNotices.vue)"""
    notices = db.query(Notice).order_by(Notice.created_at.desc()).all()
    notices_data = [NoticeResponse.from_orm(n) for n in notices]
    # NoticeResponse에 created_at이 문자열이므로 isoformat 처리 불필요
    return APIResponse(success=True, message="전체 공지사항 조회 성공", data=notices_data)


@router.delete("/notices/{notice_id}", response_model=APIResponse)
def delete_notice_by_admin(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """특정 공지사항을 삭제합니다. (AdminNotices.vue)"""
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        return APIResponse(success=False, message="해당 공지사항을 찾을 수 없습니다.")
    
    try:
        db.delete(notice)
        db.commit()
        return APIResponse(success=True, message="공지사항이 성공적으로 삭제되었습니다.", data={"notice_id": notice_id})
    except Exception as e:
        db.rollback()
        return APIResponse(success=False, message=f"공지사항 삭제 실패: {str(e)}")