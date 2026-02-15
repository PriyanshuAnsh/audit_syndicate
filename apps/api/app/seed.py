import json
from pathlib import Path

from .models import Asset, Lesson, LessonQuestion, ShopItem


ASSETS = [
    ("AAPL", "Apple", "stock", "Technology", "medium", 190),
    ("MSFT", "Microsoft", "stock", "Technology", "medium", 410),
    ("GOOGL", "Alphabet", "stock", "Technology", "medium", 170),
    ("AMZN", "Amazon", "stock", "Consumer", "medium", 180),
    ("NVDA", "NVIDIA", "stock", "Technology", "high", 850),
    ("TSLA", "Tesla", "stock", "Automotive", "high", 240),
    ("META", "Meta", "stock", "Technology", "medium", 490),
    ("JPM", "JPMorgan", "stock", "Financials", "low", 205),
    ("V", "Visa", "stock", "Financials", "low", 290),
    ("KO", "Coca-Cola", "stock", "Consumer", "low", 62),
    ("PFE", "Pfizer", "stock", "Healthcare", "low", 29),
    ("XOM", "ExxonMobil", "stock", "Energy", "medium", 114),
    ("WMT", "Walmart", "stock", "Consumer", "low", 71),
    ("DIS", "Disney", "stock", "Communication", "medium", 106),
    ("NFLX", "Netflix", "stock", "Communication", "high", 610),
    ("BTC", "Bitcoin", "crypto", "Crypto", "high", 68000),
    ("ETH", "Ethereum", "crypto", "Crypto", "high", 3500),
    ("SOL", "Solana", "crypto", "Crypto", "high", 145),
    ("ADA", "Cardano", "crypto", "Crypto", "high", 0.62),
    ("DOGE", "Dogecoin", "crypto", "Crypto", "high", 0.18),
]

SHOP_ITEMS = [
    (1, "accessory", "hat", "Leaf Cap", 60, {"image_url": "/shop/leaf-cap.svg", "pet_layer": "hat", "pet_asset": "/shop/leaf-cap.svg"}),
    (2, "accessory", "hat", "Space Helmet", 100, {"image_url": "/shop/space-helmet.svg", "pet_layer": "hat", "pet_asset": "/shop/space-helmet.svg"}),
    (3, "accessory", "glasses", "Scholar Glasses", 90, {"image_url": "/shop/scholar-glasses.svg", "pet_layer": "glasses", "pet_asset": "/shop/scholar-glasses.svg"}),
    (4, "skin", "skin", "Golden Fur", 180, {"image_url": "/shop/golden-fur.svg", "pet_layer": "skin", "pet_style": "gold"}),
    (5, "skin", "skin", "Nebula Coat", 220, {"image_url": "/shop/nebula-coat.svg", "pet_layer": "skin", "pet_style": "nebula"}),
    (6, "toy", "toy", "Coin Ball", 45, {"image_url": "/shop/coin-ball.svg", "pet_layer": "toy", "pet_asset": "/shop/coin-ball.svg"}),
    (7, "toy", "toy", "Puzzle Cube", 55, {"image_url": "/shop/puzzle-cube.svg", "pet_layer": "toy", "pet_asset": "/shop/puzzle-cube.svg"}),
    (8, "outfit", "body", "Trader Jacket", 130, {"image_url": "/shop/trader-jacket.svg", "pet_layer": "body", "pet_asset": "/shop/trader-jacket.svg"}),
    (9, "habitat", "background", "Forest Home", 200, {"image_url": "/shop/forest-home.svg", "pet_layer": "background", "pet_style": "forest"}),
    (10, "habitat", "background", "City Loft", 250, {"image_url": "/shop/city-loft.svg", "pet_layer": "background", "pet_style": "city"}),
    (11, "habitat", "background", "Moon Base", 320, {"image_url": "/shop/moon-base.svg", "pet_layer": "background", "pet_style": "moon"}),
]


BACKUP_PATH = Path(__file__).resolve().parent / "data" / "lessons_backup.json"


def load_lessons_backup() -> list[dict]:
    with BACKUP_PATH.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, list):
        raise ValueError("lessons backup must be a list")
    return payload


def seed_if_needed(db):
    if db.query(Asset).count() == 0:
        for symbol, name, asset_type, sector, risk, base_price in ASSETS:
            db.add(
                Asset(
                    symbol=symbol,
                    name=name,
                    type=asset_type,
                    sector=sector,
                    risk_class=risk,
                    base_price=base_price,
                )
            )

    lessons_payload = load_lessons_backup()
    existing_lessons = {lesson.id: lesson for lesson in db.query(Lesson).all()}

    for lesson_payload in lessons_payload:
        lesson_id = lesson_payload["id"]
        if lesson_id in existing_lessons:
            lesson = existing_lessons[lesson_id]
            lesson.title = lesson_payload["title"]
            lesson.body = lesson_payload["body"]
            lesson.reward_xp = lesson_payload.get("reward_xp", 40)
            lesson.reward_coins = lesson_payload.get("reward_coins", 50)
            lesson.quiz_json = {"source": "lesson_questions"}
        else:
            lesson = Lesson(
                id=lesson_id,
                title=lesson_payload["title"],
                body=lesson_payload["body"],
                reward_xp=lesson_payload.get("reward_xp", 40),
                reward_coins=lesson_payload.get("reward_coins", 50),
                quiz_json={"source": "lesson_questions"},
            )
            db.add(lesson)
            db.flush()

        existing_questions = {
            row.question_key: row
            for row in db.query(LessonQuestion).filter(LessonQuestion.lesson_id == lesson_id).all()
        }
        incoming_keys = set()
        for question in lesson_payload.get("questions", []):
            q_key = question["id"]
            incoming_keys.add(q_key)
            if q_key in existing_questions:
                row = existing_questions[q_key]
                row.question_text = question["question"]
                row.options_json = question["options"]
                row.answer = question["answer"]
            else:
                db.add(
                    LessonQuestion(
                        lesson_id=lesson_id,
                        question_key=q_key,
                        question_text=question["question"],
                        options_json=question["options"],
                        answer=question["answer"],
                    )
                )

        for stale_key, stale_row in existing_questions.items():
            if stale_key not in incoming_keys:
                db.delete(stale_row)

    existing_items = {item.id: item for item in db.query(ShopItem).all()}
    for item_id, item_type, slot, name, cost, metadata in SHOP_ITEMS:
        if item_id in existing_items:
            item = existing_items[item_id]
            item.type = item_type
            item.slot = slot
            item.name = name
            item.coin_cost = cost
            item.metadata_json = metadata
        else:
            db.add(
                ShopItem(
                    id=item_id,
                    type=item_type,
                    slot=slot,
                    name=name,
                    coin_cost=cost,
                    metadata_json=metadata,
                )
            )

    db.commit()
