from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Asset
from ..schemas import AssetOut, QuoteOut
from ..services import quote_for_asset


router = APIRouter(prefix="/market", tags=["market"])


@router.get("/assets", response_model=list[AssetOut])
def assets(db: Session = Depends(get_db)):
    rows = db.query(Asset).filter(Asset.is_active.is_(True)).order_by(Asset.symbol.asc()).all()
    return [
        {
            "symbol": row.symbol,
            "name": row.name,
            "type": row.type,
            "sector": row.sector,
            "risk_class": row.risk_class,
        }
        for row in rows
    ]


@router.get("/quotes", response_model=list[QuoteOut])
def quotes(db: Session = Depends(get_db)):
    rows = db.query(Asset).filter(Asset.is_active.is_(True)).all()
    payload = []
    for asset in rows:
        try:
            price, as_of = quote_for_asset(asset)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        payload.append({"symbol": asset.symbol, "price": price, "as_of": as_of})
    return payload
