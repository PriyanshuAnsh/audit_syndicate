from datetime import datetime, UTC

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Wallet(Base):
    __tablename__ = "wallets"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    cash_balance: Mapped[float] = mapped_column(Float, default=0.0)
    coins_balance: Mapped[int] = mapped_column(Integer, default=0)
    xp_total: Mapped[int] = mapped_column(Integer, default=0)


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp_current: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[str] = mapped_column(String, default="egg")
    species: Mapped[str] = mapped_column(String, default="sproutfox")
    
    # NEW FIELDS
    hunger: Mapped[int] = mapped_column(Integer, default=100)
    last_hunger_tick: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    


class Asset(Base):
    __tablename__ = "assets"

    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    sector: Mapped[str] = mapped_column(String)
    risk_class: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    base_price: Mapped[float] = mapped_column(Float, default=100.0)


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("user_id", "symbol", name="uq_user_symbol"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_cost: Mapped[float] = mapped_column(Float, default=0.0)


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    side: Mapped[str] = mapped_column(String)
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(String)
    quiz_json: Mapped[dict] = mapped_column(JSON)
    reward_xp: Mapped[int] = mapped_column(Integer)
    reward_coins: Mapped[int] = mapped_column(Integer)


class LessonQuestion(Base):
    __tablename__ = "lesson_questions"
    __table_args__ = (UniqueConstraint("lesson_id", "question_key", name="uq_lesson_question_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    question_key: Mapped[str] = mapped_column(String, index=True)
    question_text: Mapped[str] = mapped_column(String)
    options_json: Mapped[list] = mapped_column(JSON)
    answer: Mapped[str] = mapped_column(String)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    status: Mapped[str] = mapped_column(String, default="not_started")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ShopItem(Base):
    __tablename__ = "shop_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    slot: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    coin_cost: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[dict] = mapped_column(JSON, default={})


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_inventory_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("shop_items.id"))
    acquired_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)


class RewardEvent(Base):
    __tablename__ = "reward_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str] = mapped_column(String)
    xp_delta: Mapped[int] = mapped_column(Integer)
    coin_delta: Mapped[int] = mapped_column(Integer)
    ref_type: Mapped[str] = mapped_column(String)
    ref_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
