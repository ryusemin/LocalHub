import sqlite3
import json
from fastapi import APIRouter, HTTPException, UploadFile, File

admin = APIRouter(prefix="/api/admin", tags=["Admin"])

@admin.post("/load-data")
async def load_data(file: UploadFile = File(...)):
    """
    TourAPI 4.0 원본 스키마 구조의 JSON 파일을 업로드 받아 DB에 저장합니다.
    """
    # 1. 파일 확장자 검사
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="JSON 파일만 업로드할 수 있습니다.")

    # 2. 파일 내용 읽기 및 파싱
    try:
        contents = await file.read()
        payload = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="유효하지 않은 JSON 형식입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")

    db_name = "ggb_tour_data.db"
    conn = None
    inserted_count = 0

    # 3. DB 적재 로직 (make_db.py 기반)
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_types (
            content_type_id INTEGER PRIMARY KEY,
            region TEXT NOT NULL,
            content_type TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tour_items (
            content_id TEXT PRIMARY KEY,
            content_type_id INTEGER,
            title TEXT NOT NULL,
            addr1 TEXT,
            addr2 TEXT,
            zipcode TEXT,
            tel TEXT,
            mapx REAL,
            mapy REAL,
            mlevel TEXT,
            areacode TEXT,
            sigungucode TEXT,
            created_time TEXT,
            modified_time TEXT,
            first_image TEXT,
            first_image2 TEXT,
            cat1 TEXT, cat2 TEXT, cat3 TEXT,
            lDongRegnCd TEXT, lDongSignguCd TEXT,
            lclsSystm1 TEXT, lclsSystm2 TEXT, lclsSystm3 TEXT,
            cpyrhtDivCd TEXT,
            FOREIGN KEY (content_type_id) REFERENCES content_types (content_type_id)
        );
        """)
        
        # 상위 카테고리 정보 삽입 (payload가 딕셔너리 형태이므로 ['key'] 방식으로 접근)
        cursor.execute("""
            INSERT OR IGNORE INTO content_types (content_type_id, region, content_type)
            VALUES (?, ?, ?)
        """, (int(payload.get("contentTypeId", 0)), payload.get("region", ""), payload.get("contentType", "")))
        
        items_to_insert = []
        for item in payload.get("items", []):
            try:
                mapx = float(item["mapx"]) if item.get("mapx") else None
                mapy = float(item["mapy"]) if item.get("mapy") else None
            except ValueError:
                mapx, mapy = None, None

            items_to_insert.append((
                item.get("contentid"),
                int(item["contenttypeid"]) if item.get("contenttypeid") else None,
                item.get("title", "이름없음"),
                item.get("addr1"), item.get("addr2"), item.get("zipcode"), item.get("tel"),
                mapx, mapy, item.get("mlevel"), item.get("areacode"), item.get("sigungucode"),
                item.get("createdtime"), item.get("modifiedtime"),
                item.get("firstimage"), item.get("firstimage2"),
                item.get("cat1"), item.get("cat2"), item.get("cat3"),
                item.get("lDongRegnCd"), item.get("lDongSignguCd"),
                item.get("lclsSystm1"), item.get("lclsSystm2"), item.get("lclsSystm3"),
                item.get("cpyrhtDivCd")
            ))
            
        cursor.executemany("""
            INSERT OR IGNORE INTO tour_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, items_to_insert)
        
        conn.commit()
        inserted_count = len(items_to_insert)
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"데이터 삽입 중 오류가 발생했습니다: {str(e)}")
        
    finally:
        if conn:
            conn.close()

    # 명세서에 지정된 응답 포맷 반환
    return {
        "message": f"'{file.filename}' 파일의 데이터가 성공적으로 저장되었습니다.",
        "inserted_count": inserted_count
    }
