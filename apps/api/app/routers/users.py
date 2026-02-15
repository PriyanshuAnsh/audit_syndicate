from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import User, Wallet, Pet
from ..schemas import MeOut, PetOut
from ..services import apply_hunger_decay
# from ..services import pet_equipped_items

router = APIRouter(tags=["users"])


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
    pet = db.query(Pet).filter(Pet.user_id == user.id).one()
    if apply_hunger_decay(pet):
        db.commit()
        db.refresh(pet)

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
            "hunger": pet.hunger,
            "equipped_items": [],
        },
    }


@router.get("/pet", response_model=PetOut)
def get_pet(user: User = Depends(current_user), db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.user_id == user.id).one()
    return {
        "name": pet.name,
        "species": pet.species,
        "level": pet.level,
        "xp_current": pet.xp_current,
        "stage": pet.stage,
        "hunger": pet.hunger,
        # "equipped_items": pet_equipped_items(db, user.id),
        "equipped_items": [],
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
