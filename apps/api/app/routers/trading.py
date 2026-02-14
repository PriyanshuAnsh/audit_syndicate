from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import Asset, Position, Trade, User, Wallet
from ..schemas import PortfolioOut, TradeRequest
from ..services import grant_reward, portfolio_snapshot, quote_for_asset


router = APIRouter(tags=["trading"])


@router.post("/trades/buy")
def buy(payload: TradeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.symbol == payload.symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")

    try:
        price, _ = quote_for_asset(asset)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    cost = round(price * payload.quantity, 2)

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
    if wallet.cash_balance < cost:
        raise HTTPException(status_code=400, detail="insufficient cash")

    position = (
        db.query(Position)
        .filter(Position.user_id == user.id, Position.symbol == asset.symbol)
        .first()
    )
    if not position:
        position = Position(user_id=user.id, symbol=asset.symbol, quantity=0, avg_cost=0)
        db.add(position)
        db.flush()

    total_old = position.quantity * position.avg_cost
    total_new = total_old + cost
    position.quantity += payload.quantity
    position.avg_cost = total_new / position.quantity

    wallet.cash_balance = round(wallet.cash_balance - cost, 2)
    db.add(Trade(user_id=user.id, symbol=asset.symbol, side="buy", qty=payload.quantity, price=price))

    grant_reward(
        db,
        user.id,
        "trade",
        settings.reward_trade_xp,
        settings.reward_trade_coins,
        "trade",
        f"buy:{asset.symbol}:{uuid4().hex}",
    )
    db.commit()
    return {"ok": True, "symbol": asset.symbol, "price": price, "quantity": payload.quantity}


@router.post("/trades/sell")
def sell(payload: TradeRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.symbol == payload.symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")

    position = (
        db.query(Position)
        .filter(Position.user_id == user.id, Position.symbol == asset.symbol)
        .first()
    )
    if not position or position.quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="insufficient quantity")

    try:
        price, _ = quote_for_asset(asset)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    proceeds = round(price * payload.quantity, 2)

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
    wallet.cash_balance = round(wallet.cash_balance + proceeds, 2)

    position.quantity -= payload.quantity
    if position.quantity <= 0:
        db.delete(position)

    db.add(Trade(user_id=user.id, symbol=asset.symbol, side="sell", qty=payload.quantity, price=price))
    grant_reward(
        db,
        user.id,
        "trade",
        settings.reward_trade_xp,
        settings.reward_trade_coins,
        "trade",
        f"sell:{asset.symbol}:{uuid4().hex}",
    )
    db.commit()
    return {"ok": True, "symbol": asset.symbol, "price": price, "quantity": payload.quantity}


@router.get("/portfolio", response_model=PortfolioOut)
def portfolio(user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        return portfolio_snapshot(db, user.id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
