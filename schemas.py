from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 게시글 작성 요청 바디
class PostCreate(BaseModel):
    title: str
    content: str
    password: str

# 게시글 수정 요청 바디
class PostUpdate(BaseModel):
    title: str
    content: str
    password: str  # 검증용 비밀번호

# 게시글 삭제 요청 바디
class PostDelete(BaseModel):
    password: str  # 검증용 비밀번호

# API 응답 모델
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
