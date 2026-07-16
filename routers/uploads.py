from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, shutil, uuid

upload = APIRouter(prefix="/api/uploads", tags=["Uploads"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@upload.post("/")
async def upload_image(file: UploadFile = File(...)):
    # 간단 검증
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # 반환: 클라이언트에서 기준으로 사용할 경로
    return JSONResponse({"url": f"/static/uploads/{filename}"})
