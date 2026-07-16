from fastapi import HTTPException, status
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, sessionmaker
from typing import List
from dotenv import load_dotenv
from os import getenv

from models import Base, Post, Tag, TourSpot
from .schemas import StoreMatchResponse

import re

load_dotenv()
POSTS_DB_URL = getenv("POSTS_DB_URL")

engine = create_engine(POSTS_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# [B] 관광/맛집 정보 전용 DB (A DB - ggb_tour_data.db)
# ⚠️ ggb_tour_data.db 파일의 실제 상대/절대 경로에 맞게 적어주세요.
TOUR_DB_URL = getenv("TOUR_DB_URL")
tour_engine = create_engine(TOUR_DB_URL, connect_args={"check_same_thread": False})
TourSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tour_engine)

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# [B] 관광/맛집 DB 세션 의존성
def get_tour_db():
    db = TourSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 헬퍼 함수 ---

# 게시글 조회 헬퍼 함수
def get_post(post_id: int, db: Session) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return post

# 비밀번호 검증 헬퍼 함수
def verify_post_password(post: Post, password: str):
    if post.password != password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")

# 태그 처리 헬퍼 함수
def process_tags(db: Session, tag_names: List[str]):
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)
    return tags

# 게시글 상세 응답 포맷팅 헬퍼 함수
def format_post_detail(post: Post):
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "views": post.views,
        "likes": len(post.likes),
        "bookmarks": len(post.bookmarks),
        "tags": [t.name for t in post.tags],
        "image_urls": [i.image_url for i in post.images],
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

# ==========================================
# 3. 💡 [수정] 본문 텍스트에서 관광/맛집 DB를 대조하는 헬퍼 함수
# ==========================================
def extract_stores_from_text(tour_db: Session, text: str):
    if not text:
        return []

    # 1. 비교를 위한 본문 텍스트 공백 제거 및 소문자화
    clean_text = "".join(text.split()).lower()
    
    # 2. 띄어쓰기 기준으로 본문 단어 쪼개기
    words = [re.sub(r'[^\w]', '', word) for word in text.split() if len(re.sub(r'[^\w]', '', word)) >= 2]
    
    # 3. 💡 DB의 진짜 'title' 컬럼을 기준으로 1차 필터링 쿼리 생성
    query_filters = []
    for word in words:
        query_filters.append(TourSpot.title.like(f"%{word}%"))  # 👈 TourSpot.title로 저격!
    
    try:
        if query_filters:
            # title 컬럼에 해당 단어가 포함된 가게들만 DB에서 쏙 골라옵니다.
            stores = tour_db.query(TourSpot).filter(or_(*query_filters)).all()
        else:
            stores = []
    except Exception as e:
        print(f"❌ DB 조회 실패 에러: {e}")
        return []

    matched_stores = []

    # 4. 정밀 대조 및 딕셔너리 빌드
    for store in stores:
        if not store.title:  # 👈 store.title 값 검사
            continue
            
        db_title = store.title.strip()
        clean_store_name = "".join(db_title.split()).lower()

        # 💡 방식 A: 공백을 지운 본문 안에 가공된 가게 이름이 통째로 들어있는가?
        # 예: "리안중화요리" in "리안중화요리정말맛있었습니다..."
        if clean_store_name in clean_text:
            matched_stores.append({
                "title": store.title,  # 👈 정확한 title 값 대입
                "category": "음식점/관광지",
                "addr1": store.address or "",
                "addr2": "",
                "tel": store.tel or "",
                "first_image": store.first_image or "",
                "first_image2": store.first_image2 or "",
                "mapx": store.mapx,
                "mapy": store.mapy
            })

    return matched_stores