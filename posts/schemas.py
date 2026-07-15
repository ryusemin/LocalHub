from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 게시글 작성 요청 바디
class PostCreate(BaseModel):
    title: str
    content: str
    password: str
    tags: Optional[List[str]] = []       # 옵션: 태그 리스트
    image_urls: Optional[List[str]] = [] # 옵션: 이미지 URL 리스트

# 게시글 수정 요청 바디
class PostUpdate(BaseModel):
    password: str
    title: str
    content: str
    tags: Optional[List[str]] = []       # 옵션
    image_urls: Optional[List[str]] = [] # 옵션

# 게시글 삭제 요청 바디
class PostDelete(BaseModel):
    password: str

# 게시글 목록용 응답
class PostListResponse(BaseModel):
    id: int
    title: str
    views: int
    likes: int
    tags: List[str]
    created_at: datetime

# 💡 1. 추가: 매칭되어 반환될 가게 정보의 Pydantic 스키마 정의
class StoreMatchResponse(BaseModel):
    title: str
    category: str
    addr1: str
    addr2: str = ""
    tel: str = ""
    first_image: str = ""
    first_image2: str = ""
    mapx: Optional[float] = None
    mapy: Optional[float] = None

    class Config:
        from_attributes = True

# 게시글 상세용 응답
# 수정: 상세 응답에 matched_stores 필드 추가
class PostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    views: int
    likes: int
    bookmarks: int
    tags: List[str]
    image_urls: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 이 글에서 발견된 가게들의 정보 리스트 (기본값은 빈 배열)
    matched_stores: List[StoreMatchResponse] = []

    class Config:
        from_attributes = True
