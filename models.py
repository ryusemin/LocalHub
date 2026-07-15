from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 태그 N:M 관계 연결 테이블
post_tag_association = Table(
    'post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True) # 게시글 ID
    title = Column(String(255), nullable=False) # 게시글 제목
    content = Column(Text, nullable=False) # 게시글 내용
    password = Column(String(50), nullable=False) # 게시글 비밀번호 (수정/삭제 시 검증용)
    views = Column(Integer, default=0) # 조회수
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 생성일
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # 수정일

    # 관계 설정 (Cascade 적용)
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan") # 게시글 이미지
    tags = relationship("Tag", secondary=post_tag_association, back_populates="posts") # 게시글 태그
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan") # 게시글 좋아요
    bookmarks = relationship("Bookmark", back_populates="post", cascade="all, delete-orphan") # 게시글 북마크

class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(Integer, primary_key=True, index=True) # 게시글 이미지 ID
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE")) # 게시글 ID (외래키)
    image_url = Column(String(500), nullable=False) # 이미지 URL
    post = relationship("Post", back_populates="images") # 게시글과의 관계 설정

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True) # 태그 ID
    name = Column(String(50), unique=True, index=True, nullable=False) # 태그 이름
    posts = relationship("Post", secondary=post_tag_association, back_populates="tags") # 태그와 게시글의 관계 설정

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True) # 좋아요 ID
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE")) # 게시글 ID (외래키)
    client_id = Column(String(255)) # 클라이언트 식별자
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 좋아요 생성일
    post = relationship("Post", back_populates="likes") # 게시글과의 관계 설정

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True) # 북마크 ID
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE")) # 게시글 ID (외래키)
    client_id = Column(String(255)) # 클라이언트 식별자
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 북마크 생성일
    post = relationship("Post", back_populates="bookmarks") # 게시글과의 관계 설정


# 💡 챗봇의 tool_response 구조와 100% 싱크를 맞춘 가게 정보 테이블
# models.py 파일에서 TourSpot 클래스 부분만 아래와 같이 수정합니다.

# models.py 파일 내의 TourSpot 모델
class TourSpot(Base):
    __tablename__ = "tour_items"
    
    content_id = Column(String(50), primary_key=True, index=True) 
    
    # 💡 [핵심] 변수명과 DB 컬럼명을 모두 'title'로 일치시킵니다!
    title = Column(String(255), nullable=False, index=True) 
    
    # 주소 컬럼도 실제 DB명이 addr1이라면 아래처럼 name="addr1"을 주거나 변수명을 addr1로 맞춥니다.
    address = Column(String(500), name="addr1", nullable=True)          
    
    category = Column(String(100), name="cat1", nullable=True) 
    tel = Column(String(50), nullable=True)
    first_image = Column(String(500), nullable=True)
    first_image2 = Column(String(500), nullable=True)
    mapx = Column(Float, nullable=True)
    mapy = Column(Float, nullable=True)