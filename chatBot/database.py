import os
import sqlite3
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "ggb_tour_data.db")

def search_tour_db(category: Optional[str], keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
    if not keyword:
        return []

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