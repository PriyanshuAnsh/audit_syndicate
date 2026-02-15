from datetime import datetime, timezone
import hashlib
import logging
from time import time

import httpx
from sqlalchemy.orm import Session

from .config import settings
from .models import Asset, Inventory, Pet, Position, RewardEvent, ShopItem, Wallet

# Hunger constant
HUNGER_DECAY_PER_DAY = 10

LEVEL_THRESHOLDS = [0, 100, 250, 450, 700, 1000, 1400, 1850]
STAGE_BY_LEVEL = {
    1: "egg",
    3: "baby",
    5: "teen",
    7: "adult",
}

logger = logging.getLogger(__name__)
_quote_cache: dict[str, tuple[float, float]] = {}
FINNHUB_CRYPTO_SYMBOL_MAP = {
    "BTC": "BINANCE:BTCUSDT",
    "ETH": "BINANCE:ETHUSDT",
    "SOL": "BINANCE:SOLUSDT",
    "ADA": "BINANCE:ADAUSDT",
    "DOGE": "BINANCE:DOGEUSDT",
}


def stage_for_level(level: int) -> str:
    stage = "egg"
    for milestone, name in sorted(STAGE_BY_LEVEL.items()):
        if level >= milestone:
            stage = name
    return stage


def compute_level(total_xp: int) -> tuple[int, int]:
    level = 1
    for idx, threshold in enumerate(LEVEL_THRESHOLDS, start=1):
        if total_xp >= threshold:
            level = idx
    current_threshold = LEVEL_THRESHOLDS[min(level - 1, len(LEVEL_THRESHOLDS) - 1)]
    xp_current = max(0, total_xp - current_threshold)
    return level, xp_current


def quote_for_asset(asset: Asset) -> tuple[float, datetime]:
    if settings.price_mode in {"finnhub", "hybrid"}:
        finnhub_symbol = _finnhub_symbol_for_asset(asset)
        live = _quote_from_finnhub(finnhub_symbol)
        if live is not None:
            return round(live, 2), datetime.now(timezone.utc).replace(tzinfo=None)
        if settings.price_mode == "finnhub":
            raise RuntimeError(f"live quote unavailable for {asset.symbol}")

    return _simulated_quote(asset)


def _simulated_quote(asset: Asset) -> tuple[float, datetime]:
    now = datetime.now(timezone.utc)
    minute_bucket = now.strftime("%Y%m%d%H%M")
    digest = hashlib.sha256(f"{asset.symbol}:{minute_bucket}".encode()).hexdigest()
    drift_seed = int(digest[:8], 16)
    change = ((drift_seed % 1201) - 600) / 10000.0
    price = max(0.5, round(asset.base_price * (1 + change), 2))
    return price, now.replace(tzinfo=None)


def _quote_from_finnhub(symbol: str) -> float | None:
    if not settings.finnhub_api_key:
        return None

    now_ts = time()
    cached = _quote_cache.get(symbol)
    if cached and (now_ts - cached[1]) < settings.price_cache_ttl_seconds:
        return cached[0]

    try:
        response = httpx.get(
            f"{settings.finnhub_base_url}/quote",
            params={"symbol": symbol, "token": settings.finnhub_api_key},
            timeout=4.0,
        )
        response.raise_for_status()
        payload = response.json()
        current_price = payload.get("c")
        if isinstance(current_price, (int, float)) and current_price > 0:
            price = float(current_price)
            _quote_cache[symbol] = (price, now_ts)
            return price
    except Exception as exc:
        logger.warning("finnhub request failed for %s: %s", symbol, exc)
    return None


def _finnhub_symbol_for_asset(asset: Asset) -> str:
    if asset.type == "crypto":
        return FINNHUB_CRYPTO_SYMBOL_MAP.get(asset.symbol, asset.symbol)
    return asset.symbol


def grant_reward(db: Session, user_id: int, source: str, xp: int, coins: int, ref_type: str, ref_id: str):
    exists = (
        db.query(RewardEvent)
        .filter(
            RewardEvent.user_id == user_id,
            RewardEvent.source == source,
            RewardEvent.ref_type == ref_type,
            RewardEvent.ref_id == ref_id,
        )
        .first()
    )
    if exists:
        return

    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).one()
    wallet.xp_total += xp
    wallet.coins_balance += coins

    pet = db.query(Pet).filter(Pet.user_id == user_id).one()
    new_level, xp_current = compute_level(wallet.xp_total)
    pet.level = new_level
    pet.xp_current = xp_current
    pet.stage = stage_for_level(new_level)

    db.add(
        RewardEvent(
            user_id=user_id,
            source=source,
            xp_delta=xp,
            coin_delta=coins,
            ref_type=ref_type,
            ref_id=ref_id,
        )
    )


def portfolio_snapshot(db: Session, user_id: int) -> dict:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).one()
    positions = db.query(Position).filter(Position.user_id == user_id).all()

    line_items = []
    invested_total = 0.0
    market_total = 0.0

    for position in positions:
        if position.quantity <= 0:
            continue
        asset = db.query(Asset).filter(Asset.symbol == position.symbol).one()
        price, _ = quote_for_asset(asset)
        market_value = round(position.quantity * price, 2)
        cost_value = round(position.quantity * position.avg_cost, 2)
        unrealized_pl = round(market_value - cost_value, 2)
        invested_total += cost_value
        market_total += market_value
        line_items.append(
            {
                "symbol": position.symbol,
                "quantity": position.quantity,
                "avg_cost": round(position.avg_cost, 2),
                "market_price": price,
                "market_value": market_value,
                "unrealized_pl": unrealized_pl,
            }
        )

    total_value = round(wallet.cash_balance + market_total, 2)
    total_pl = round(market_total - invested_total, 2)

    for item in line_items:
        item["allocation_pct"] = round((item["market_value"] / total_value) * 100, 2) if total_value > 0 else 0

    concentration = max([i["allocation_pct"] for i in line_items], default=0)
    diversification = round(max(0, 100 - concentration), 2)

    return {
        "cash": round(wallet.cash_balance, 2),
        "total_value": total_value,
        "total_pl": total_pl,
        "diversification_score": diversification,
        "positions": line_items,
    }


def pet_equipped_items(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(Inventory, ShopItem)
        .join(ShopItem, ShopItem.id == Inventory.item_id)
        .filter(Inventory.user_id == user_id, Inventory.equipped.is_(True))
        .all()
    )
    return [
        {
            "item_id": item.id,
            "name": item.name,
            "slot": item.slot,
            "type": item.type,
            "metadata_json": item.metadata_json or {},
        }
        for _, item in rows
    ]

def apply_hunger_decay(pet):
    now = datetime.now(UTC).replace(tzinfo=None)
    last = pet.last_hunger_tick

    days_passed = (now - last).days

    if days_passed > 0:
        pet.hunger = max(0, pet.hunger - days_passed * HUNGER_DECAY_PER_DAY)
        pet.last_hunger_tick = now

    return pet