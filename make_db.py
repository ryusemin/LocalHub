import sqlite3
import json
import os

# 팀원들과 공유하신 8개의 JSON 파일 이름 목록입니다.
json_files = [
    "구미_경북권_관광지.json",
    "구미_경북권_문화시설.json",
    "구미_경북권_축제공연행사.json",
    "구미_경북권_여행코스.json",
    "구미_경북권_레포츠.json",
    "구미_경북권_숙박.json",
    "구미_경북권_쇼핑.json",
    "구미_경북권_음식점.json"
]

db_name = "ggb_tour_data.db"

print("🚀 SQLite 데이터베이스 생성 및 데이터 적재를 시작합니다...")

# 1. DB 연결 및 테이블 생성
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
conn.commit()

total_inserted = 0

# 2. JSON 파일 파싱 및 데이터 삽입
for file_name in json_files:
    if not os.path.exists(file_name):
        print(f"⚠️ {file_name} 파일이 현재 폴더에 없습니다. 건너뜁니다.")
        continue
        
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 상위 카테고리 정보 삽입
    cursor.execute("""
        INSERT OR IGNORE INTO content_types (content_type_id, region, content_type)
        VALUES (?, ?, ?)
    """, (int(data["contentTypeId"]), data["region"], data["contentType"]))
    
    # 상세 항목 삽입
    items_to_insert = []
    for item in data["items"]:
        # mapx, mapy 실수형(Float) 변환 및 예외 처리
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
    print(f"✅ {data['contentType']} 데이터 ({len(items_to_insert)}건) 변환 및 적재 완료!")
    total_inserted += len(items_to_insert)

conn.close()
print(f"\n🎉 작업 완료! 총 {total_inserted}건의 데이터가 포함된 '{db_name}' 파일이 생성되었습니다.")