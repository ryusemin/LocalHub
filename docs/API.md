### 🌐 LocalHub API 명세서 (v1.0)

#### 1. 공통 응답 포맷 (예시)
모든 API는 기본적으로 JSON 형태로 응답하며, 성공 시 상태 코드 200(또는 201)을 반환합니다.

```json
{
  "message": "성공/실패 메시지",
  "data": { ... } // 실제 응답 데이터
}
```

---

#### 2. 게시판 (Posts) API - CRUD 및 추가기능

| 기능 | HTTP Method | Endpoint (URI) | 파라미터 및 요청 바디 (Request) | 응답 데이터 (Response) |
| :--- | :---: | :--- | :--- | :--- |
| **게시글 목록 조회** | `GET` | `/api/posts` | **[Query]**<br>`page`: 페이지 번호 (기본: 1)<br>`limit`: 한 페이지 개수 (기본: 10)<br>`keyword`: 검색어 (옵션)<br>`tag`: 태그 필터링 (옵션) | `[ { id, title, views, likes, tags, created_at } ... ]`<br>`total_count` (전체 글 수) |
| **게시글 상세 조회** | `GET` | `/api/posts/{post_id}` | **[Path]**<br>`post_id`: 게시글 고유 ID | `{ id, title, content, views, likes, bookmarks, tags, image_urls, created_at }`<br>*(호출 시 자동으로 조회수+1)* |
| **게시글 작성** | `POST` | `/api/posts` | **[Body] JSON**<br>`title`: 제목<br>`content`: 본문<br>`password`: 수정/삭제용 비밀번호(평문)<br>`tags`: `["맛집", "구미"]` (옵션)<br>`image_urls`: `["url1"]` (옵션) | `post_id` (생성된 게시글 ID) |
| **비밀번호 검증**<br>*(수정/삭제 권한)* | `POST` | `/api/posts/{post_id}/verify` | **[Body] JSON**<br>`password`: 입력한 비밀번호 | `{ "is_valid": true/false }` |
| **게시글 수정** | `PUT` | `/api/posts/{post_id}` | **[Body] JSON**<br>`password`: 검증용 비밀번호<br>`title`: 수정할 제목<br>`content`: 수정할 본문<br>`tags`, `image_urls` (옵션) | 수정한 게시글 정보 (상세 조회 포맷과 동일) |
| **게시글 삭제** | `DELETE` | `/api/posts/{post_id}` | **[Body] JSON**<br>`password`: 검증용 비밀번호 | `{ "message": "삭제되었습니다." }` |
| **좋아요 토글** | `POST` | `/api/posts/{post_id}/like` | - | `{ "likes": 15 }` (업데이트된 좋아요 수) |
| **북마크 토글** | `POST` | `/api/posts/{post_id}/bookmark` | - | `{ "bookmarked": true/false }` |

---

#### 3. 챗봇 (Chatbot) API - 필수 요구사항

| 기능 | HTTP Method | Endpoint (URI) | 파라미터 및 요청 바디 (Request) | 응답 데이터 (Response) |
| :--- | :---: | :--- | :--- | :--- |
| **지역 정보 질의응답** | `POST` | `/api/chat` | **[Body] JSON**<br>`message`: 사용자 입력 메시지<br>`history`: `[{"role":"user", "content":"..."}]`<br>*(옵션: 이전 대화 문맥 유지용)* | `{ "reply": "다가오는 구미 축제는..." }`<br>*(OpenAI API 연동 결과물)* |

---

#### 4. 외부 서비스 연동 API (Should / Could have)

| 기능 | HTTP Method | Endpoint (URI) | 파라미터 및 요청 바디 (Request) | 응답 데이터 (Response) |
| :--- | :---: | :--- | :--- | :--- |
| **날씨 정보 조회** | `GET` | `/api/weather` | **[Query]**<br>`region`: 지역명 | `{ "region": "구미", "temperature": 30.08, "feels_like": 34.75, "humidity": 68, "weather_description": "온흐림", "is_suitable_for_travel": true, "status_message": "..." }` |

---

#### 5. 관리자 (Admin) API - 데이터 초기화

| 기능 | HTTP Method | Endpoint (URI) | 파라미터 및 요청 바디 (Request) | 응답 데이터 (Response) |
| :--- | :---: | :--- | :--- | :--- |
| **초기 데이터 DB 저장**<br>*(관리자용)* | `POST` | `/api/admin/load-data` | **[Body] JSON**<br>TourAPI 4.0 원본 스키마 구조 수신 | `{"message": "데이터가 성공적으로 저장되었습니다.", "inserted_count": 150}` |
