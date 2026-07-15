from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from sqlalchemy.ext.declarative import declarative_base

# 💡 [핵심 해결책] Base를 두 개로 명확히 나눕니다.
Base = declarative_base()      # 게시글용 Base (posts.db에 자동 생성될 대상)
TourBase = declarative_base()  # 맛집용 Base (이미 데이터가 존재하므로 posts.db에 자동 생성되면 안 됨!)

# 태그 N:M 관계 연결 테이블
post_tag_association = Table(
    'post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(50), nullable=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tag_association, back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="post", cascade="all, delete-orphan")

class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    post = relationship("Post", back_populates="images")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    posts = relationship("Post", secondary=post_tag_association, back_populates="tags")

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    client_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    post = relationship("Post", back_populates="likes")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    client_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    post = relationship("Post", back_populates="bookmarks")


# 💡 [핵심 해결책] TourSpot은 Base가 아닌 'TourBase'를 상속받습니다.
# 이렇게 하면 Base.metadata.create_all(bind=engine)를 실행해도 posts.db에 절대로 자동 생성되지 않습니다!
class TourSpot(TourBase):
    __tablename__ = "tour_items"
    
    content_id = Column(String(50), primary_key=True, index=True) 
    title = Column(String(255), nullable=False, index=True) 
    address = Column(String(500), name="addr1", nullable=True)          
    category = Column(String(100), name="cat1", nullable=True) 
    tel = Column(String(50), nullable=True)
    first_image = Column(String(500), nullable=True)
    first_image2 = Column(String(500), nullable=True)
    mapx = Column(Float, nullable=True)
    mapy = Column(Float, nullable=True)