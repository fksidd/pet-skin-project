from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import httpx
import os

from app.database import get_db
from app.db_models import Hospital
from app.schemas import APIResponse

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

# 청주시 동물병원 검색 키워드
HOSPITAL_KEYWORDS = [
    "동물병원", "수의과병원", "동물의료센터", "동물메디컬센터",
    "종합동물병원", "펫클리닉", "가축병원", "수의진료소",
    "애니멀클리닉", "반려동물병원", "펫메디컬", "24시동물병원"
]

@router.get("/cheongju")
async def get_cheongju_hospitals(
    limit: int = Query(50, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """청주시 동물병원 검색 (거리 계산 제거)"""
    
    try:
        # 1. 자체 DB에서 청주시 병원 검색
        db_results = await search_cheongju_from_database(limit, db)
        
        # 2. 카카오 Places API에서 추가 검색
        kakao_results = await search_cheongju_from_kakao_api()
        
        # 3. 결과 병합 및 중복 제거
        merged_results = merge_cheongju_results(db_results, kakao_results, limit)
        
        return {
            "success": True,
            "message": f"청주시에서 {len(merged_results)}개의 동물병원을 찾았습니다.",
            "data": merged_results
        }
        
    except Exception as e:
        print(f"청주시 병원 검색 오류: {e}")
        return {
            "success": False,
            "message": "병원 검색 중 오류가 발생했습니다.",
            "data": []
        }

async def search_cheongju_from_database(limit: int, db: Session):
    """자체 데이터베이스에서 청주시 병원 검색"""
    
    # 키워드 조건 생성
    keyword_conditions = " OR ".join([f"name LIKE '%{keyword}%'" for keyword in HOSPITAL_KEYWORDS])
    
    query = text(f"""
        SELECT *
        FROM hospitals
        WHERE address LIKE '%청주%'
        AND ({keyword_conditions})
        ORDER BY name
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    
    hospitals = []
    for row in result:
        hospitals.append({
            "id": row.id,
            "place_name": row.name,
            "address_name": row.address,
            "phone": row.phone or "",
            "lat": row.lat,
            "lng": row.lng,
            "is_24hour": row.is_24hour,
            "source": "database"
        })
    
    return hospitals

async def search_cheongju_from_kakao_api():
    """카카오 Places API에서 청주시 병원 검색"""
    
    kakao_api_key = os.getenv("KAKAO_REST_API_KEY")
    if not kakao_api_key:
        return []
    
    all_results = []
    
    async with httpx.AsyncClient() as client:
        # 청주시 특화 키워드로 검색
        cheongju_keywords = [
            "청주 동물병원", "청주시 수의과", "청주 펫클리닉",
            "청주 동물의료센터", "흥덕구 동물병원", "서원구 동물병원",
            "청원구 동물병원", "상당구 동물병원"
        ]
        
        for keyword in cheongju_keywords:
            try:
                response = await client.get(
                    "https://dapi.kakao.com/v2/local/search/keyword.json",
                    headers={"Authorization": f"KakaoAK {kakao_api_key}"},
                    params={
                        "query": keyword,
                        "size": 15
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get("documents", [])
                    
                    for place in documents:
                        # 청주시 주소 필터링
                        if "청주" in place.get('address_name', ''):
                            # 동물병원 관련 카테고리 필터링
                            if any(word in place.get('category_name', '') for word in ["동물", "수의", "병원"]):
                                all_results.append({
                                    "id": f"kakao_{place['id']}",
                                    "place_name": place["place_name"],
                                    "address_name": place["address_name"],
                                    "phone": place.get("phone", ""),
                                    "lat": float(place["y"]),
                                    "lng": float(place["x"]),
                                    "is_24hour": "24시" in place["place_name"],
                                    "source": "kakao"
                                })
                            
            except Exception as e:
                print(f"카카오 API 검색 오류 ({keyword}): {e}")
                continue
    
    return all_results

def merge_cheongju_results(db_results: List[dict], kakao_results: List[dict], limit: int):
    """청주시 결과 병합 및 중복 제거 (이름순 정렬)"""
    
    merged = []
    seen_places = set()
    
    # DB 결과 우선 추가
    for hospital in db_results:
        key = f"{hospital['place_name']}_{hospital['address_name']}"
        if key not in seen_places:
            merged.append(hospital)
            seen_places.add(key)
    
    # 카카오 결과 추가 (중복 제거)
    for hospital in kakao_results:
        key = f"{hospital['place_name']}_{hospital['address_name']}"
        if key not in seen_places:
            merged.append(hospital)
            seen_places.add(key)
    
    # 이름순 정렬 (거리 대신)
    merged.sort(key=lambda x: x['place_name'])
    
    return merged[:limit]

@router.get("/emergency/cheongju")
async def get_cheongju_emergency_hospitals(
    db: Session = Depends(get_db)
):
    """청주시 24시간 응급 진료 가능한 동물병원 검색"""
    
    query = text("""
        SELECT *
        FROM hospitals
        WHERE address LIKE '%청주%'
        AND is_24hour = true
        ORDER BY name
        LIMIT 20
    """)
    
    result = db.execute(query)
    
    hospitals = []
    for row in result:
        hospitals.append({
            "id": row.id,
            "place_name": row.name,
            "address_name": row.address,
            "phone": row.phone or "",
            "lat": row.lat,
            "lng": row.lng,
            "is_24hour": True
        })
    
    return {
        "success": True,
        "data": hospitals
    }

@router.post("/add")
async def add_hospital(
    name: str,
    address: str,
    lat: float,
    lng: float,
    phone: str = "",
    is_24hour: bool = False,
    db: Session = Depends(get_db)
):
    """새 동물병원 정보 추가"""
    
    # 중복 체크
    existing = db.query(Hospital).filter(
        Hospital.name == name,
        Hospital.address == address
    ).first()
    
    if existing:
        return {
            "success": False,
            "message": "이미 등록된 병원입니다."
        }
    
    # 새 병원 추가
    hospital = Hospital(
        name=name,
        address=address,
        phone=phone,
        lat=lat,
        lng=lng,
        is_24hour=is_24hour
    )
    
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    
    return {
        "success": True,
        "message": "동물병원이 성공적으로 등록되었습니다.",
        "data": {
            "id": hospital.id,
            "name": hospital.name
        }
    }