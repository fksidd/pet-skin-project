import requests
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db_models import Hospital

def import_public_data():
    """공공데이터 포털의 동물병원 데이터 가져오기"""
    # 행정안전부 동물병원 파일데이터 다운로드 후 처리
    df = pd.read_csv('동물병원_data.csv', encoding='cp949')
    
    # 필요한 열 추출 및 가공
    hospitals = []
    for _, row in df.iterrows():
        # 청주시 데이터 필터링
        if '청주시' in row['소재지주소']:
            # 위경도 변환 (좌표계 변환 필요할 수 있음)
            hospitals.append({
                'name': row['사업장명'],
                'address': row['소재지주소'],
                'phone': row['전화번호'] if '전화번호' in df.columns else '',
                'lat': float(row['위도']) if not pd.isna(row['위도']) else 0,
                'lng': float(row['경도']) if not pd.isna(row['경도']) else 0,
                'is_24hour': False  # 기본값
            })
    
    # DB에 저장
    db = SessionLocal()
    try:
        for hospital_data in hospitals:
            hospital = Hospital(**hospital_data)
            db.add(hospital)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"데이터 저장 오류: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_public_data()