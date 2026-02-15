from datetime import datetime, timezone
import hashlib
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
    now = datetime.now(timezone.utc)
    minute_bucket = now.strftime("%Y%m%d%H%M")
    digest = hashlib.sha256(f"{asset.symbol}:{minute_bucket}".encode()).hexdigest()
    drift_seed = int(digest[:8], 16)
    change = ((drift_seed % 1201) - 600) / 10000.0
    price = max(0.5, round(asset.base_price * (1 + change), 2))
    return price, now.replace(tzinfo=None)


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