from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # 💡 [핵심] 클래스에 없는 변수(OpenAI 관련 변수 등)가 들어와도 에러 내지 말고 무시하라는 뜻!