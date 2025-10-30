"""
Seed the database with a large, strictly time-ascending event stream via HTTP.
- Creates ~150 grocery products.
- Emits random purchases, sales, price changes, updates, promotions, and notes.
- All events are globally time-ordered from 2024-01-01 up to current time.

Run:
    python /Users/corido/Desktop/SmartMarket/server/seed_data.py
"""
from __future__ import annotations
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import random
import string
from datetime import datetime, timedelta
import requests

BASE_URL = os.getenv("SMARTMARKET_BASE_URL", "http://localhost:8000")
CMD = f"{BASE_URL}/command"

def rand_name() -> str:
    adjectives = ["Fresh", "Organic", "Whole", "Classic", "Premium", "Family", "Local", "Italian", "Greek", "Spicy", "Mild", "Low-Fat", "Sugar-Free"]
    nouns = [
        "Milk", "Eggs", "Bread", "Cheese", "Yogurt", "Butter", "Chicken Breast", "Ground Beef", "Salmon Fillet",
        "Apples", "Bananas", "Oranges", "Tomatoes", "Cucumbers", "Lettuce", "Potatoes", "Onions", "Garlic",
        "Rice", "Pasta", "Olive Oil", "Sunflower Oil", "Flour", "Sugar", "Salt", "Black Pepper",
        "Tuna Cans", "Beans", "Chickpeas", "Cornflakes", "Oatmeal", "Chocolate Bar", "Coffee", "Tea",
        "Soda", "Orange Juice", "Water 1.5L", "Chips", "Crackers", "Granola", "Ketchup", "Mustard", "Mayonnaise",
        "Dish Soap", "Laundry Detergent", "Toilet Paper", "Paper Towels", "Trash Bags"
    ]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

def rand_brand() -> str:
    return random.choice([
        "Acme", "FreshCo", "GreenFarm", "DailyBest", "Sunrise", "Valley", "GoodTaste",
        "PureLife", "BlueOcean", "GoldenField", "FamilyChoice", "Chef's", "HomeStyle"
    ])

def rand_category() -> str:
    return random.choice([
        "Dairy", "Bakery", "Produce", "Meat", "Seafood", "Pantry", "Beverages",
        "Snacks", "Household", "Condiments", "Breakfast"
    ])

def rand_image_url() -> str:
    token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"https://img.example.com/{token}.jpg"

# Varied notes: positive, negative, neutral, operational
NOTES = [
    "Customer favorite; sales trending up",
    "Fresh batch received; quality rated A",
    "Short-dated inventory; monitor sell-through",
    "Packaging damage reported on some units",
    "Supplier delay; restock ETA next week",
    "Shelf relocated to aisle 5",
    "Barcode updated; verify at POS",
    "Price tag updated at shelf",
    "Seasonal placement started",
    "Inventory audit variance adjusted",
    "Promotion scheduled for weekend",
    "BOGO promo ended",
    "Overstock moved to backroom",
    "Planogram reset complete",
    "Backorder cleared",
    "Return rate within normal range",
    "Storage temperature verified",
    "Organic certification verified",
    "Gluten-free label updated",
    "Bundle SKU created",
    "Online exclusive flag toggled",
    "Discontinued notice posted",
    "Supplier switched to local",
    "Margin review complete",
    "Shrinkage observed; investigate",
    "Mis-scan issue fixed",
    "Loyalty points bonus active",
    "Sampling event scheduled",
    "Endcap display approved",
    "Recall check completed; no issues found",
    "Sustainability message added to label",
    # extra variety
    "Customer complaint: odd smell reported on one unit",
    "Excellent shelf presence; high visibility",
    "Price perceived as fair by most shoppers",
    "Minor label misprint identified",
    "Supplier quality audit passed",
    "Sell-through slightly below forecast",
    "Restock completed; inventory healthy",
    "Promo sign missing; replaced by staff",
    "Great tasting notes from sampling booth",
    "Damaged carton returned to supplier",
]

def rand_note() -> str:
    return random.choice(NOTES)

def iso(dt: datetime) -> str:
    # Format as naive ISO seconds; server stores as provided
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def post(path: str, payload: dict):
    r = requests.post(f"{CMD}{path}", json=payload, timeout=30)
    if not r.ok:
        print(f"POST {path} failed: {r.status_code} {r.text}")

def put(path: str, payload: dict):
    r = requests.put(f"{CMD}{path}", json=payload, timeout=30)
    if not r.ok:
        print(f"PUT {path} failed: {r.status_code} {r.text}")

def delete(path: str, payload: dict):
    r = requests.delete(f"{CMD}{path}", json=payload, timeout=30)
    if not r.ok:
        print(f"DELETE {path} failed: {r.status_code} {r.text}")

def generate_product_id(year_key: str, idx: int) -> str:
    # Short product IDs, e.g., G24-0001
    return f"G{year_key[2:4]}-{idx:04d}"

def seed(num_products: int = 150) -> None:
    """
    Build all events first, then assign globally ascending timestamps from 2024-01-01 to now.
    """
    random.seed(42)

    # 1) Build event list without time
    events: list[tuple[str, str, dict]] = []  # (method, path, payload_without_time)

    start_anchor = datetime(2024, 1, 1, 8, 0, 0)
    year_key = start_anchor.strftime("%Y%m%d%H%M%S")

    for i in range(num_products):
        pid = generate_product_id(year_key, i + 1)
        name = rand_name()
        brand = rand_brand()
        category = rand_category()
        qty = random.randint(20, 300)
        cost = round(random.uniform(0.5, 40.0), 2)
        margin = random.uniform(1.10, 1.80)
        price = round(max(0.1, cost * margin), 2)

        # CREATE
        events.append((
            "POST",
            "/product/create",
            {
                "product_id": pid,
                "name": name,
                "current_price": price,
                "cost_price": cost,
                "quantity": qty,
                "brand": brand,
                "category": category,
                "is_on_promotion": False,
                "promotion_discount_percent": 0.0,
                "image_url": rand_image_url(),
                "note": rand_note(),
            },
        ))

        # Random actions (server handles business rules)
        steps = random.randint(10, 22)
        for _ in range(steps):
            action = random.choices(
                population=["purchase", "sale", "price", "update", "promo", "note"],
                weights=[30, 30, 15, 10, 10, 5],
                k=1,
            )[0]

            if action == "purchase":
                q = random.randint(5, 60)
                unit_cost = round(cost * random.uniform(0.9, 1.15), 2)
                events.append((
                    "POST",
                    f"/product/{pid}/purchase",
                    {
                        "quantity": q,
                        "purchase_unit_cost": unit_cost,
                    },
                ))

            elif action == "sale":
                q = random.randint(1, 12)
                sale_price = round(price * random.uniform(0.9, 1.1), 2)
                events.append((
                    "POST",
                    f"/product/{pid}/sale",
                    {
                        "quantity": q,
                        "sale_unit_price": sale_price,
                        "sale_unit_cost": cost,
                    },
                ))

            elif action == "price":
                if random.random() < 0.7:
                    new_price = round(max(0.1, price * random.uniform(0.92, 1.12)), 2)
                    events.append((
                        "POST",  # keep POST to avoid 405
                        f"/product/{pid}/change_price",
                        { "current_price": new_price },
                    ))
                    price = new_price
                else:
                    new_cost = round(max(0.05, cost * random.uniform(0.95, 1.08)), 2)
                    events.append((
                        "POST",
                        f"/product/{pid}/change_price",
                        { "cost_price": new_cost },
                    ))
                    cost = new_cost

            elif action == "update":
                fields = {}
                if random.random() < 0.3:
                    fields["name"] = rand_name()
                if random.random() < 0.4:
                    fields["brand"] = rand_brand()
                if random.random() < 0.4:
                    fields["category"] = rand_category()
                if random.random() < 0.4:
                    fields["image_url"] = rand_image_url()
                if random.random() < 0.5:
                    fields["note"] = rand_note()
                if fields:
                    events.append((
                        "PUT",
                        f"/product/{pid}/update",
                        { "fields": fields },
                    ))

            elif action == "promo":
                on = random.random() < 0.5
                discount = round(random.uniform(5.0, 40.0), 2) if on else 0.0
                events.append((
                    "POST",
                    f"/product/{pid}/set_promotion",
                    {
                        "is_on_promotion": on,
                        "promotion_discount_percent": discount,
                    },
                ))

            elif action == "note":
                events.append((
                    "POST",
                    f"/product/{pid}/add_note",
                    { "note": rand_note() },
                ))

        # Occasionally delete at the end for this product
        if random.random() < 0.1:
            events.append((
                "DELETE",
                f"/product/{pid}/delete",
                {},
            ))

    # 2) Assign strictly increasing timestamps from 2024-01-01 to now
    total_events = len(events)
    if total_events == 0:
        print("No events to send.")
        return

    start_time = datetime(2024, 1, 1, 8, 0, 0)
    end_time = datetime.now()

    delta = end_time - start_time
    sent = 0

    # 3) Send events over HTTP with strictly increasing occurred_at_utc
    for idx, (method, path, payload) in enumerate(events):
        if total_events == 1:
            t = start_time
        else:
            frac = idx / (total_events - 1)
            t = start_time + timedelta(seconds=delta.total_seconds() * frac)

        body = dict(payload)
        body["occurred_at_utc"] = iso(t)

        try:
            if method == "POST":
                post(path, body)
            elif method == "PUT":
                put(path, body)
            elif method == "DELETE":
                delete(path, body)
            sent += 1
        except Exception as e:
            print(f"{method} {path} failed at {body['occurred_at_utc']}: {e}")

    print(f"Seeded {sent} events across ~{num_products} grocery products.")
    print(f"Time range: {start_time.isoformat()} -> {end_time.isoformat()}")

if __name__ == "__main__":
    seed(150)
