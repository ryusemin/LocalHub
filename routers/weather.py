import httpx
from os import getenv
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

weather = APIRouter(prefix="/api/weather", tags=["Weather"])

# OpenWeatherMap API Key 로드
OPENWEATHER_API_KEY = getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 경북권 주요 권역별 위/경도 좌표 및 한글명 매핑
REGION_COORDINATES = {
    "구미": {"lat": 36.1194, "lon": 128.3445},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "칠곡군": {"lat": 36.0167, "lon": 128.3833},
    "성주군": {"lat": 35.9500, "lon": 128.4333},
    "고령군": {"lat": 35.8000, "lon": 128.3500},
    "경주": {"lat": 35.8562, "lon": 129.2132},
    "안동": {"lat": 36.5683, "lon": 128.7294},
    "포항": {"lat": 36.0190, "lon": 129.3435},
    "울릉도": {"lat": 37.4844, "lon": 130.9022}
}

# 응답 스키마 정의
class WeatherSuitabilityResponse(BaseModel):
    region: str
    temperature: float
    feels_like: float
    humidity: int
    weather_description: str
    is_suitable_for_travel: bool
    status_message: str

# 날씨 상태 코드, 온도, 풍속 등을 바탕으로 여행 적합 여부(is_suitable_for_travel) 판단
# weather_id: 2xx 뇌우, 3xx 이슬비, 5xx 비, 6xx 눈
def evaluate_travel_suitability(temp: float, weather_id: int, wind_speed: float) -> tuple[bool, str]:
    # 1. 극단적인 날씨 상황 (폭풍우, 폭설, 비 등)
    if 200 <= weather_id < 600:
        return False, "비나 뇌우가 예보되어 있어 야외 여행에 부적합합니다. 실내 관광 위주로 계획해 보세요."
    if 600 <= weather_id < 700:
        return False, "폭설 또는 눈이 내려 도로 결빙 및 안전 위험이 있습니다."
    
    # 2. 강풍 발생 시 (풍속 10 m/s 이상)
    if wind_speed >= 10.0:
        return False, "바람이 매우 강하게 불어 야외 활동 시 안전에 유의해야 합니다."

    # 3. 극단적인 기온 (폭염 또는 한파)
    if temp >= 35.0:
        return False, "기온이 매우 높은 폭염 날씨입니다. 충분한 수분 섭취와 실내 휴식을 권장합니다."
    if temp <= -10.0:
        return False, "영하 10도 이하의 극심한 한파입니다. 장시간 야외 활동은 피해주세요."

    # 4. 적합한 날씨
    return True, "여행하기 좋은 날씨입니다! 즐거운 여행 되세요."

@weather.get("", response_model=WeatherSuitabilityResponse, name="권역별 날씨 및 여행 적합도 조회")
async def get_region_weather(
    region: str = Query(..., description="조회할 권역명")
):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="OpenWeatherMap API Key가 설정되어 있지 않습니다."
        )

    # 1. 권역 매핑 확인
    if region not in REGION_COORDINATES:
        if region == "구미시":
            region = "구미"
        elif region in ["대구광역시", "대구시"]:
            region = "대구"
        elif region == "칠곡":
            region = "칠곡군"
        elif region == "성주":
            region = "성주군"
        elif region == "고령":
            region = "고령군"
        elif region == "경주시":
            region = "경주"
        elif region == "안동시":
            region = "안동"
        elif region == "포항시":
            region = "포항"
        elif region == "울릉도":
            region = "울릉도"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 권역입니다. 지원 권역: {list(REGION_COORDINATES.keys())}"
            )
    
    coords = REGION_COORDINATES[region]

    # 2. 외부 API 호출을 위한 파라미터 구성
    params = {
        "lat": coords["lat"],
        "lon": coords["lon"],
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # 섭씨 온도 사용
        "lang": "kr"        # 한국어 설명
    }

    # 3. httpx를 사용한 비동기 외부 API 연동
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params, timeout=5.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="외부 날씨 API 호출 중 오류가 발생했습니다."
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"날씨 서버 연결 실패: {str(exc)}"
            )

    weather_data = response.json()

    # 4. 데이터 파싱
    try:
        main_info = weather_data["main"]
        temp = main_info["temp"]
        feels_like = main_info["feels_like"]
        humidity = main_info["humidity"]
        
        weather_details = weather_data["weather"][0]
        weather_id = weather_details["id"]
        weather_desc = weather_details["description"]
        
        wind_speed = weather_data.get("wind", {}).get("speed", 0.0)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="날씨 API 응답 포맷이 올바르지 않습니다."
        )

    # 5. 여행 적합도 평가
    is_suitable, status_msg = evaluate_travel_suitability(temp, weather_id, wind_speed)

    # 6. 결과 반환
    return WeatherSuitabilityResponse(
        region=region,
        temperature=temp,
        feels_like=feels_like,
        humidity=humidity,
        weather_description=weather_desc,
        is_suitable_for_travel=is_suitable,
        status_message=status_msg
    )
