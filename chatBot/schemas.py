from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    reply: str              # 📱 유저 화면 표시용 (가게 이름 없는 깔끔한 멘트)
    history_reply: str      # 💾 다음 대화 history 저장용 (가게 이름 포함)
    tool_response: Optional[List[Dict[str, Any]]]