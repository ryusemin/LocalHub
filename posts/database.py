from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import List
from dotenv import load_dotenv
from os import getenv

from models import Base, Post, Tag

load_dotenv()
DATABASE_URL = getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
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
