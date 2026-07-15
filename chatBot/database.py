import os
import sqlite3
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "ggb_tour_data.db")

def search_tour_db(
    category: Optional[str], 
    keyword: str, 
    region: Optional[str] = None,  # 💡 [변경] 상위 행정구역(지역) 필터 인자 추가
    limit: int = 5
) -> List[Dict[str, Any]]:
    if not keyword:
        return []

    # 기본 검색 쿼리 (키워드 기반 검색)
    query = """
        SELECT
            t.title,
            t.addr1,
            t.addr2,
            t.tel,
            t.first_image,
            t.first_image2,
            t.mapx,
            t.mapy,
            c.content_type
        FROM tour_items AS t
        LEFT JOIN content_types AS c
            ON t.content_type_id = c.content_type_id
        WHERE (
            t.title LIKE ?
            OR t.addr1 LIKE ?
            OR t.addr2 LIKE ?
            OR t.cat1 LIKE ?
            OR t.cat2 LIKE ?
            OR t.cat3 LIKE ?
        )
    """
    params = [f"%{keyword}%"] * 6

    # 💡 [핵심 추가] AI가 '구미', '대구' 같은 상위 지역명을 확실히 짚었다면 주소에서 한 번 더 걸러줌
    if region:
        query += "\n AND (t.addr1 LIKE ? OR t.addr2 LIKE ?)"
        params.extend([f"%{region}%", f"%{region}%"])

    if category:
        query += "\n AND c.content_type LIKE ?"
        params.append(f"%{category}%")

    query += "\n ORDER BY t.title COLLATE NOCASE LIMIT ?"
    params.append(limit)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    results = []
    for row in rows:
        results.append({
            "title": row["title"],
            "category": row["content_type"],
            "addr1": row["addr1"],
            "addr2": row["addr2"],
            "tel": row["tel"],
            "first_image": row["first_image"],
            "first_image2": row["first_image2"],
            "mapx": row["mapx"],
            "mapy": row["mapy"],
        })

    return results