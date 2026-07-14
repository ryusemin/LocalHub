from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

from models import Base, Post, PostImage, Tag, Like, Bookmark
from schemas import PostCreate, PostUpdate, PostDelete, PostListResponse, PostDetailResponse
from settings import Settings

settings = Settings()

# --- DB 설정 ---
LOCALHUB_DATABASE_URL = settings.database_url
engine = create_engine(LOCALHUB_DATABASE_URL, connect_args={"check_same_thread": False})
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

@app.get("/api/posts", response_model=List[PostListResponse], name="게시글 목록 조회")
def read_posts(
    page: int = 1, 
    limit: int = 10, 
    keyword: Optional[str] = None, 
    tag: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    if keyword:
        query = query.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    if tag:
        query = query.filter(Post.tags.any(Tag.name == tag))
        
    skip = (page - 1) * limit
    posts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "title": p.title,
            "views": p.views,
            "likes": len(p.likes),
            "tags": [t.name for t in p.tags],
            "created_at": p.created_at
        } for p in posts
    ]

@app.get("/api/posts/{post_id}", response_model=PostDetailResponse, name="게시글 상세 조회")
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(post_id, db)
    
    post.views += 1
    db.commit()
    db.refresh(post)
    
    return format_post_detail(post)

@app.post("/api/posts", status_code=status.HTTP_201_CREATED, name="게시글 작성")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content, password=post.password)
    
    db_post.tags = process_tags(db, post.tags)
    db_post.images = [PostImage(image_url=url) for url in post.image_urls]
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"post_id": db_post.id}

@app.put("/api/posts/{post_id}", response_model=PostDetailResponse, name="게시글 수정")
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)):
    db_post = get_post(post_id, db)
    verify_post_password(db_post, post_data.password)

    db_post.title = post_data.title
    db_post.content = post_data.content
    db_post.tags = process_tags(db, post_data.tags)
    
    db.query(PostImage).filter(PostImage.post_id == post_id).delete()
    db_post.images = [PostImage(image_url=url) for url in post_data.image_urls]

    db.commit()
    db.refresh(db_post)
    return format_post_detail(db_post)

@app.delete("/api/posts/{post_id}", name="게시글 삭제")
def delete_post(post_id: int, post_data: PostDelete, db: Session = Depends(get_db)):
    db_post = get_post(post_id, db)
    verify_post_password(db_post, post_data.password)

    db.delete(db_post)
    db.commit()
    return {"message": "삭제되었습니다."}

@app.post("/api/posts/{post_id}/like", name="좋아요 토글")
def toggle_like(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = get_post(post_id, db)
    client_id = request.client.host
    
    existing_like = db.query(Like).filter(Like.post_id == post_id, Like.client_id == client_id).first()
    
    if existing_like:
        db.delete(existing_like)
    else:
        new_like = Like(post_id=post_id, client_id=client_id)
        db.add(new_like)
        
    db.commit()
    return {"likes": len(post.likes)}

@app.post("/api/posts/{post_id}/bookmark", name="북마크 토글")
def toggle_bookmark(post_id: int, request: Request, db: Session = Depends(get_db)):
    get_post(post_id, db) # 게시물 존재 여부 확인
    client_id = request.client.host
    
    existing_bookmark = db.query(Bookmark).filter(Bookmark.post_id == post_id, Bookmark.client_id == client_id).first()
    
    if existing_bookmark:
        db.delete(existing_bookmark)
        bookmarked = False
    else:
        new_bookmark = Bookmark(post_id=post_id, client_id=client_id)
        db.add(new_bookmark)
        bookmarked = True
        
    db.commit()
    return {"bookmarked": bookmarked}

# --- 헬퍼 함수 ---

# 게시글 조회 헬퍼 함수
def get_post(post_id: int, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return post

# 게시글 비밀번호 검증 헬퍼 함수
def verify_post_password(post: Post, password: str):
    if post.password != password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")

# 게시글 태그 처리 헬퍼 함수
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
