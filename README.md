# LocalHub

## 팀원 소개

| 이름 | GitHub | 담당 역할 |
|---|---|---|
| <img src="https://github.com/ryusemin.png" width="60"><br>류세민 | [@ryusemin](https://github.com/ryusemin) | BE<br>(챗봇/배포) |
| <img src="https://github.com/qkrwns1478.png" width="60"><br>박준식 | [@qkrwns1478](https://github.com/qkrwns1478) | BE<br>(게시판/날씨) |
| <img src="https://github.com/ongdikk.png" width="60"><br>이동익 | [@ongdikk](https://github.com/ongdikk) | FE |

## 배포 URL

- 프론트엔드: https://local-hub-gumi4-6.netlify.app/
- 백엔드: https://localhub-yejf.onrender.com/

---

## 실행 방법

```bash
# 가상환경 실행 (Bash)
source venv/Scripts/activate

# 가상환경 실행 (CMD)
venv/Scripts/activate.bat

# 필수 의존성 설치
pip install -r requirements.txt

# main.py 실행
uvicorn main:app --reload
```

---

## 문서

| 문서 | 설명 |
| :--- | :--- |
| [API 명세](./docs/API.md) | 전체 API 엔드포인트 및 요청/응답 형식 |
| [DB 명세](./docs/DB.md) | 지역권 데이터셋 DB 설계 및 구조 |
| [ERD 명세](./docs/ERD.md) | DB 테이블 구조 및 ERD |
| [챗봇 명세](./docs/CHATBOT.md) | 챗봇 시나리오 명세 |

---

## MVP 정의서

| 구분 | 내용 |
| :--- | :--- |
| **선정 권역** | 구미/경북 |
| **핵심 문제** | 지역 정보의 파편화로 인해 주민 및 관광객이 유용한 정보를 쉽게 공유하고 찾을 수 있는 통합 커뮤니티 부재 |
| **타깃 사용자** | 구미/경북 지역 주민 및 해당 지역을 방문하는 관광객 |
| **성공 지표** | 익명 기반 커뮤니티 기능(CRUD) 및 지역 정보 챗봇이 실제 배포 환경(Netlify/Render)에서 원활하게 정상 동작하는 것 |

### Must have (반드시 포함 - 개발 의뢰 문서(RFP) 필수 요구사항)
* 제공된 JSON 파일 기반 데이터 연동 (프론트/백엔드 모두 적용, 공공 API 직접 호출 X)
* 익명 기반 1개 권역 카테고리 게시판 기능 (목록 조회, 상세 조회, 작성, 수정, 삭제)
* 게시글 작성 시 수정용 비밀번호 평문 저장 및 일치 여부 기반의 권한 확인 로직 구현
* FastAPI 엔드포인트(`/api/chat`) 및 OpenAI API 활용 자연어 지역 정보 질의응답 챗봇 구현
* Vue.js 기반 프론트엔드 구성 및 FastAPI + SQLite(DB) 활용 백엔드 구축
* 민감 정보 `.env` 분리 및 프론트엔드(Netlify), 백엔드(Render) 연동 외부 접근 배포

### Should / Could have (선택 - 팀이 선정한 기능으로 교체)
* 커뮤니티 게시판 추가기능 (조회수 표시, 게시글 검색, 북마크, 좋아요, 이미지 첨부, 태그 기능 등)
* 날씨 정보 연동 (외부 API를 활용한 권역별 현재 날씨 및 여행 적합 여부 표시) (선택)

### Won't have (이번 MVP 범위에서 제외 - 스코프 크립: 범위가 계속 늘어나는 현상 방지)
* 지도 시각화 (API 기반 관광지·맛집 지도 핀 시각화 및 권역 필터 기능 제외)
* 소셜 공유 연동 (카카오톡 링크 복사 등 플랫폼 공유 및 OG 태그 제외)
* 축제 캘린더 (권역별 축제 일정을 캘린더 형태로 시각화하는 기능 제외)
* 데이터 시각화 대시보드 (게시글 현황 및 인기 지역 통계 등 시각화 제외)
* 다국어 지원 (i18n을 활용한 한/영 전환 기능 제외)
* 실시간 알림 (WebSocket 기반 알림 및 접속자 현황 표시 제외)
* 경로 안내 (복수의 장소를 선택하여 이동 경로를 지도 위에 그리는 기능 제외)
