from .models import Asset, Lesson, ShopItem


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

LESSONS = [
    {
        "id": 1,
        "title": "Diversification Basics",
        "body": "Diversification means spreading investments across assets to reduce concentration risk.",
        "quiz_json": [
            {
                "id": "q1",
                "question": "What does diversification reduce?",
                "options": ["Concentration risk", "All market risk", "Taxes"],
                "answer": "Concentration risk",
            },
            {
                "id": "q2",
                "question": "Is diversification guaranteed profit?",
                "options": ["Yes", "No"],
                "answer": "No",
            },
        ],
    },
    {
        "id": 2,
        "title": "Risk vs Reward",
        "body": "Higher potential return typically comes with higher volatility and drawdown risk.",
        "quiz_json": [
            {
                "id": "q1",
                "question": "Higher return potential usually means:",
                "options": ["Lower risk", "Higher risk"],
                "answer": "Higher risk",
            },
            {
                "id": "q2",
                "question": "A healthy habit is to:",
                "options": ["Bet all on one asset", "Review allocation regularly"],
                "answer": "Review allocation regularly",
            },
        ],
    },
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

    if db.query(Lesson).count() == 0:
        for lesson in LESSONS:
            db.add(
                Lesson(
                    id=lesson["id"],
                    title=lesson["title"],
                    body=lesson["body"],
                    quiz_json=lesson["quiz_json"],
                    reward_xp=40,
                    reward_coins=50,
                )
            )

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
