from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List

from models import Base, Post
from schemas import PostCreate, PostUpdate, PostDelete, PostResponse
from settings import Settings

settings = Settings()

# --- DB 설정 ---
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API")

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.get("/")
def root():
    return "Welcome to LocalHub! This is the main page of the LocalHub API."

# 게시글 목록 조회
@app.get("/api/posts", response_model=List[PostResponse])
def read_posts(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

# 게시글 상세 조회
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return post

# 게시글 작성
@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content, password=post.password)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# 게시글 수정
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
        
    # 권한 확인: 평문 비밀번호 일치 여부 검증
    if db_post.password != post_data.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")
        
    db_post.title = post_data.title
    db_post.content = post_data.content
    db.commit()
    db.refresh(db_post)
    return db_post

# 게시글 삭제
@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, post_data: PostDelete, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
        
    # 권한 확인: 평문 비밀번호 일치 여부 검증
    if db_post.password != post_data.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")
        
    db.delete(db_post)
    db.commit()
    return {"message": "삭제되었습니다."}
