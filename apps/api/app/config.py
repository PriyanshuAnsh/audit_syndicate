import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "InvestiPet API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_minutes: int = 60 * 24 * 7
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./investipet.db")
    cors_origins: list[str] = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
    trusted_hosts: list[str] = [host.strip() for host in os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if host.strip()]
    enable_docs: bool = os.getenv("ENABLE_DOCS", "true").lower() == "true"
    force_https: bool = os.getenv("FORCE_HTTPS", "false").lower() == "true"

    starter_cash: float = 10000.0
    starter_coins: int = 500

    reward_daily_login_xp: int = 15
    reward_daily_login_coins: int = 20
    reward_trade_xp: int = 10
    reward_trade_coins: int = 10
    reward_lesson_complete_xp: int = 40
    reward_lesson_complete_coins: int = 50
    reward_quiz_perfect_xp: int = 20
    reward_quiz_perfect_coins: int = 25


settings = Settings()
