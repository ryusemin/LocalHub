import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "ggb_tour_data.db")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 또는 환경 변수를 확인해 주세요.")

app = FastAPI(title="LocalHub Tour Chat API")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    reply: str
    tool_response: Optional[List[Dict[str, Any]]] = None


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


def _get_message(choice: Any) -> Dict[str, Any]:
    if isinstance(choice, dict):
        return choice.get("message", {}) or {}
    if hasattr(choice, "message"):
        return choice.message or {}
    return {}


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "LocalHub Tour Chat API is running."}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    messages = [
        {
            "role": "system",
            "content": (
                "너는 구미/경북권 관광 데이터베이스에 대한 전문 답변을 제공하는 챗봇이야. "
                "사용자가 장소, 음식점, 여행지, 숙박, 축제 등의 정보를 물으면 반드시 search_tour_db 함수를 호출해서 SQLite DB를 조회해야 해. "
                "DB에서 가져온 데이터만을 바탕으로 자연스럽고 친절한 한국어 답변을 만들어줘."
            ),
        }
    ]

    if request.history:
        messages.extend(request.history)

    messages.append({"role": "user", "content": request.message})

    function_definition = {
        "name": "search_tour_db",
        "description": "구미/경북권 tour_items 데이터베이스에서 장소를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "검색할 한글 카테고리 이름(예: 음식점, 관광지, 숙박, 쇼핑, 레포츠, 문화시설, 축제공연행사, 여행코스)."
                },
                "keyword": {
                    "type": "string",
                    "description": "검색할 지역명, 장소명 또는 키워드(예: 인동, 구미, 맛집, 카페 등)."
                }
            },
            "required": ["keyword"]
        }
    }

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            functions=[function_definition],
            function_call="auto",
            temperature=0.2,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI 호출 오류: {exc}")

    choice = response.choices[0]
    message = _get_message(choice)
    function_call = message.get("function_call")

    if not function_call:
        reply = message.get("content", "죄송하지만 요청을 처리할 수 없습니다.")
        return ChatResponse(reply=reply, tool_response=None)

    arguments = function_call.get("arguments")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="OpenAI 함수 호출 인수 파싱 실패")

    category = arguments.get("category")
    keyword = arguments.get("keyword")
    if not keyword:
        raise HTTPException(status_code=400, detail="keyword 값이 필요합니다.")

    results = search_tour_db(category=category, keyword=keyword, limit=5)
    function_result = json.dumps({"results": results}, ensure_ascii=False)

    messages.append({"role": "assistant", "content": None, "function_call": function_call})
    messages.append({"role": "function", "name": "search_tour_db", "content": function_result})

    try:
        final_response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI 후속 호출 오류: {exc}")

    final_choice = final_response.choices[0]
    final_message = _get_message(final_choice)
    reply = final_message.get("content", "DB에서 결과를 찾았지만 답변을 생성하지 못했습니다.")

    return ChatResponse(reply=reply, tool_response=results)
