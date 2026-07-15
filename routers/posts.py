from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from posts.database import get_db, get_post, verify_post_password, process_tags, format_post_detail
from posts.schemas import PostCreate, PostUpdate, PostDelete, PostListResponse, PostDetailResponse
from models import Post, PostImage, Tag, Like, Bookmark

posts = APIRouter(prefix="/api/posts", tags=["Posts"])

@posts.post("", status_code=status.HTTP_201_CREATED, name="게시글 작성")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content, password=post.password)
    
    db_post.tags = process_tags(db, post.tags)
    db_post.images = [PostImage(image_url=url) for url in post.image_urls]
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"post_id": db_post.id}

@posts.get("", response_model=List[PostListResponse], name="게시글 목록 조회")
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
    db_posts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "title": p.title,
            "views": p.views,
            "likes": len(p.likes),
            "tags": [t.name for t in p.tags],
            "created_at": p.created_at
        } for p in db_posts
    ]

@posts.get("/{post_id}", response_model=PostDetailResponse, name="게시글 상세 조회")
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(post_id, db)
    
    post.views += 1
    db.commit()
    db.refresh(post)
    
    return format_post_detail(post)

@posts.put("/{post_id}", response_model=PostDetailResponse, name="게시글 수정")
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

@posts.delete("/{post_id}", name="게시글 삭제")
def delete_post(post_id: int, post_data: PostDelete, db: Session = Depends(get_db)):
    db_post = get_post(post_id, db)
    verify_post_password(db_post, post_data.password)

    db.delete(db_post)
    db.commit()
    return {"message": "삭제되었습니다."}

@posts.post("/{post_id}/like", name="좋아요 토글")
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

@posts.post("/{post_id}/bookmark", name="북마크 토글")
def toggle_bookmark(post_id: int, request: Request, db: Session = Depends(get_db)):
    get_post(post_id, db) 
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
