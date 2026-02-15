from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import User, Wallet, Pet, Position
from ..schemas import MeOut, PetOut
from datetime import datetime, UTC
# from ..services import pet_equipped_items


router = APIRouter(tags=["users"])

HUNGER_DECAY_PER_WEEK = 5  # % of hunger lost per week

def compute_current_hunger(pet: Pet) -> int:
    """Calculate current hunger based on last_hunger_tick and decay per week."""
    print(f"[DEBUG] --- compute_current_hunger ---")
    print(f"[DEBUG] Pet.hunger stored in DB: {pet.hunger}")
    print(f"[DEBUG] Pet.last_hunger_tick: {pet.last_hunger_tick}")

    if not pet.last_hunger_tick:
        print(f"[DEBUG] No last_hunger_tick, returning hunger as-is: {pet.hunger}")
        return pet.hunger

    now = datetime.now(UTC).replace(tzinfo=None)
    elapsed_weeks = (now - pet.last_hunger_tick).days // 7
    print(f"[DEBUG] Weeks elapsed since last tick: {elapsed_weeks}")

    computed_hunger = max(0, pet.hunger - elapsed_weeks * HUNGER_DECAY_PER_WEEK)
    print(f"[DEBUG] Computed current hunger: {computed_hunger}")
    return computed_hunger


def compute_financial_health(user: User, db: Session) -> int:
    """Compute financial health (0-100) from wallet and positions."""
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    positions = db.query(Position).filter(Position.user_id == user.id).all()

    if not wallet:
        return 80  # fallback

    # Simple example: combine cash, coins, and position value into a percentage
    cash_score = min(wallet.cash_balance / 1000, 1)
    coins_score = min(wallet.coins_balance / 100, 1)
    position_score = 0
    if positions:
        position_score = min(sum(p.avg_cost * p.quantity for p in positions) / 1000, 1)

    health = int((cash_score + coins_score + position_score) / 3 * 100)
    return health


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
    pet = db.query(Pet).filter(Pet.user_id == user.id).one()

    current_hunger = compute_current_hunger(pet)
    financial_health = compute_financial_health(user, db)

    return {
        "email": user.email,
        "cash_balance": wallet.cash_balance,
        "coins_balance": wallet.coins_balance,
        "xp_total": wallet.xp_total,
        "pet": {
            "name": pet.name,
            "species": pet.species,
            "level": pet.level,
            "xp_current": pet.xp_current,
            "stage": pet.stage,
            "hunger": current_hunger,
            # "equipped_items": pet_equipped_items(db, user.id),
            "equipped_items": [],
        },
    }


@router.get("/pet", response_model=PetOut)
def get_pet(user: User = Depends(current_user), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.user_id == user.id).one()
    current_hunger = compute_current_hunger(pet)
    return {
        "name": pet.name,
        "species": pet.species,
        "level": pet.level,
        "xp_current": pet.xp_current,
        "stage": pet.stage,
        # "equipped_items": pet_equipped_items(db, user.id),
        "equipped_items": [],
        "hunger": current_hunger,
    }


@router.get("/pet/family")
def pet_family(user: User = Depends(current_user), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.user_id == user.id).one()
    return {
        "primary_pet": pet.name,
        "family_slots": [
            {"slot": 1, "unlocked": pet.level >= 4},
            {"slot": 2, "unlocked": pet.level >= 6},
        ],
    }
