from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
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