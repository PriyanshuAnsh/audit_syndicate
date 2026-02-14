from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Inventory, RewardEvent, ShopItem, User, Wallet
from ..schemas import EquipRequest, PurchaseRequest


router = APIRouter(tags=["economy"])


@router.get("/rewards/balance")
def rewards_balance(user: User = Depends(current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
    return {"xp_total": wallet.xp_total, "coins_balance": wallet.coins_balance}


@router.get("/rewards/history")
def rewards_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(RewardEvent)
        .filter(RewardEvent.user_id == user.id)
        .order_by(RewardEvent.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "source": row.source,
            "xp_delta": row.xp_delta,
            "coin_delta": row.coin_delta,
            "ref_type": row.ref_type,
            "ref_id": row.ref_id,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/shop/items")
# def shop_items(db: Session = Depends(get_db)):
#     rows = db.query(ShopItem).order_by(ShopItem.id.asc()).all()
#     return [
#         {
#             "id": row.id,
#             "type": row.type,
#             "slot": row.slot,
#             "name": row.name,
#             "coin_cost": row.coin_cost,
#             "metadata_json": row.metadata_json,
#         }
#         for row in rows
#     ]
def shop_items():
    raise HTTPException(status_code=503, detail="shop is temporarily disabled")


@router.post("/shop/purchase")
# def purchase(payload: PurchaseRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
#     item = db.query(ShopItem).filter(ShopItem.id == payload.item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="item not found")
#
#     wallet = db.query(Wallet).filter(Wallet.user_id == user.id).one()
#     if wallet.coins_balance < item.coin_cost:
#         raise HTTPException(status_code=400, detail="insufficient coins")
#
#     existing = (
#         db.query(Inventory)
#         .filter(Inventory.user_id == user.id, Inventory.item_id == item.id)
#         .first()
#     )
#     if existing:
#         return {"ok": True, "already_owned": True}
#
#     wallet.coins_balance -= item.coin_cost
#     db.add(Inventory(user_id=user.id, item_id=item.id, equipped=False))
#     db.commit()
#     return {"ok": True, "already_owned": False}
def purchase():
    raise HTTPException(status_code=503, detail="shop is temporarily disabled")


@router.get("/inventory")
# def inventory(user: User = Depends(current_user), db: Session = Depends(get_db)):
#     rows = (
#         db.query(Inventory, ShopItem)
#         .join(ShopItem, ShopItem.id == Inventory.item_id)
#         .filter(Inventory.user_id == user.id)
#         .all()
#     )
#     return [
#         {
#             "item_id": item.id,
#             "name": item.name,
#             "type": item.type,
#             "slot": item.slot,
#             "equipped": inv.equipped,
#         }
#         for inv, item in rows
#     ]
def inventory():
    raise HTTPException(status_code=503, detail="shop is temporarily disabled")


@router.post("/pet/equip")
# def equip(payload: EquipRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
#     inv = (
#         db.query(Inventory)
#         .filter(Inventory.user_id == user.id, Inventory.item_id == payload.item_id)
#         .first()
#     )
#     if not inv:
#         raise HTTPException(status_code=400, detail="item not owned")
#
#     target_item = db.query(ShopItem).filter(ShopItem.id == inv.item_id).one()
#
#     for row in (
#         db.query(Inventory, ShopItem)
#         .join(ShopItem, ShopItem.id == Inventory.item_id)
#         .filter(Inventory.user_id == user.id, ShopItem.slot == target_item.slot)
#         .all()
#     ):
#         row[0].equipped = False
#
#     inv.equipped = True
#     db.commit()
#     return {"ok": True}
def equip():
    raise HTTPException(status_code=503, detail="shop is temporarily disabled")
