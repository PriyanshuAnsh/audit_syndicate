from datetime import date, datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
)
from ..config import settings
from ..database import get_db
from ..models import Pet, RefreshToken, User, Wallet
from ..schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from ..services import grant_reward


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if settings.environment != "development" and settings.jwt_secret == "dev-secret-change-me":
        raise HTTPException(status_code=500, detail="server misconfigured")

    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="email already exists")

    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()

    wallet = Wallet(user_id=user.id, cash_balance=settings.starter_cash, coins_balance=settings.starter_coins, xp_total=0)
    pet = Pet(user_id=user.id, name=payload.pet_name, level=1, xp_current=0, stage="egg", species="sproutfox")
    db.add(wallet)
    db.add(pet)
    db.flush()

    access = create_access_token(user.id)
    refresh, exp = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token=refresh, expires_at=exp))

    grant_reward(db, user.id, "daily_login", settings.reward_daily_login_xp, settings.reward_daily_login_coins, "daily", str(date.today()))
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    access = create_access_token(user.id)
    refresh, exp = create_refresh_token(user.id)
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.add(RefreshToken(user_id=user.id, token=refresh, expires_at=exp))

    grant_reward(db, user.id, "daily_login", settings.reward_daily_login_xp, settings.reward_daily_login_coins, "daily", str(date.today()))
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    record = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if not record:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    if record.expires_at < datetime.now(UTC).replace(tzinfo=None):
        db.delete(record)
        db.commit()
        raise HTTPException(status_code=401, detail="refresh token expired")

    try:
        user_id = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="invalid refresh token") from exc

    db.delete(record)
    access = create_access_token(user_id)
    new_refresh, exp = create_refresh_token(user_id)
    db.add(RefreshToken(user_id=user_id, token=new_refresh, expires_at=exp))
    db.commit()

    return TokenResponse(access_token=access, refresh_token=new_refresh)
