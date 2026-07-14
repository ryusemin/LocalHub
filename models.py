from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True) # 게시글 고유 ID (Auto Increment)
    title = Column(String(255), nullable=False)        # 게시글 제목
    content = Column(Text, nullable=False)             # 게시글 본문
    password = Column(String(50), nullable=False)      # 수정/삭제용 비밀번호 (평문)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 작성 일시
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())       # 수정 일시
