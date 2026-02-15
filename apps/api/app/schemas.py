from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    pet_name: str = Field(min_length=2, max_length=24)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TradeRequest(BaseModel):
    symbol: str
    quantity: float = Field(gt=0)


class LessonSubmitRequest(BaseModel):
    answers: dict[str, str]
    idempotency_key: str


class LessonCheckRequest(BaseModel):
    question_id: str
    answer: str


class PurchaseRequest(BaseModel):
    item_id: int


class EquipRequest(BaseModel):
    item_id: int


class AssetOut(BaseModel):
    symbol: str
    name: str
    type: str
    sector: str
    risk_class: str


class QuoteOut(BaseModel):
    symbol: str
    price: float
    as_of: datetime


class RewardEventOut(BaseModel):
    source: str
    xp_delta: int
    coin_delta: int
    ref_type: str
    ref_id: str
    created_at: datetime


class PositionOut(BaseModel):
    symbol: str
    quantity: float
    avg_cost: float
    market_price: float
    market_value: float
    unrealized_pl: float
    allocation_pct: float


class PortfolioOut(BaseModel):
    cash: float
    total_value: float
    total_pl: float
    diversification_score: float
    positions: list[PositionOut]


class LessonOut(BaseModel):
    id: int
    title: str
    body: str
    quiz: list[dict]
    question_count: int
    reward_xp: int
    reward_coins: int
    completed: bool
    score: float | None


class LessonListOut(BaseModel):
    items: list[LessonOut]
    page: int
    page_size: int
    total: int
    total_pages: int


class PetOut(BaseModel):
    name: str
    species: str
    level: int
    xp_current: int
    stage: str
    equipped_items: list[dict]


class MeOut(BaseModel):
    email: str
    cash_balance: float
    coins_balance: int
    xp_total: int
    pet: PetOut
