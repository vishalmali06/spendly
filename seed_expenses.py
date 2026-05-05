import random
import sys
from datetime import date, timedelta

from database.db import get_db


CATEGORY_CONFIG = {
    "Food": {
        "weight": 30,
        "amount_range": (50, 800),
        "descriptions": [
            "Lunch at office canteen",
            "Dinner at Sagar Ratna",
            "Swiggy order — biryani",
            "Zomato — pizza night",
            "Morning chai and samosa",
            "Groceries from Big Bazaar",
            "Vegetables from local sabzi mandi",
            "Filter coffee at Cafe Coffee Day",
            "South Indian breakfast",
            "Street food — pani puri",
        ],
    },
    "Transport": {
        "weight": 20,
        "amount_range": (20, 500),
        "descriptions": [
            "Auto rickshaw fare",
            "Ola cab to office",
            "Uber ride home",
            "Metro card recharge",
            "Petrol top-up",
            "Bus ticket",
            "Train ticket — local",
            "Parking fee",
        ],
    },
    "Bills": {
        "weight": 15,
        "amount_range": (200, 3000),
        "descriptions": [
            "Electricity bill",
            "Airtel mobile recharge",
            "Jio fiber internet",
            "Water bill",
            "DTH recharge — Tata Sky",
            "Gas cylinder refill",
            "Society maintenance",
        ],
    },
    "Shopping": {
        "weight": 15,
        "amount_range": (200, 5000),
        "descriptions": [
            "Amazon order — household",
            "Flipkart — clothes",
            "Myntra sale purchase",
            "New shirt from Westside",
            "Shoes from Bata",
            "Mobile accessories",
            "Books from Crossword",
        ],
    },
    "Other": {
        "weight": 10,
        "amount_range": (50, 1000),
        "descriptions": [
            "Salon — haircut",
            "Birthday gift",
            "Donation to temple",
            "Stationery",
            "Dry cleaning",
            "Gift wrap and card",
        ],
    },
    "Health": {
        "weight": 5,
        "amount_range": (100, 2000),
        "descriptions": [
            "Apollo pharmacy — medicines",
            "Doctor consultation",
            "Lab test — blood work",
            "Dentist visit",
            "Vitamins and supplements",
        ],
    },
    "Entertainment": {
        "weight": 5,
        "amount_range": (100, 1500),
        "descriptions": [
            "PVR movie ticket",
            "Netflix subscription",
            "Spotify premium",
            "Concert ticket",
            "BookMyShow — play",
            "Hotstar subscription",
        ],
    },
}


def parse_args(argv):
    if len(argv) != 4:
        return None
    try:
        return int(argv[1]), int(argv[2]), int(argv[3])
    except ValueError:
        return None


def main():
    parsed = parse_args(sys.argv)
    if parsed is None:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    user_id, count, months = parsed

    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        today = date.today()
        days_back = months * 30
        earliest = today - timedelta(days=days_back)

        categories = list(CATEGORY_CONFIG.keys())
        weights = [CATEGORY_CONFIG[c]["weight"] for c in categories]

        rows = []
        for _ in range(count):
            category = random.choices(categories, weights=weights, k=1)[0]
            cfg = CATEGORY_CONFIG[category]
            amount = round(random.uniform(*cfg["amount_range"]), 2)
            description = random.choice(cfg["descriptions"])
            offset = random.randint(0, days_back)
            d = (earliest + timedelta(days=offset)).isoformat()
            rows.append((user_id, amount, category, d, description))

        try:
            with conn:
                conn.executemany(
                    "INSERT INTO expenses (user_id, amount, category, date, description) "
                    "VALUES (?, ?, ?, ?, ?)",
                    rows,
                )
        except Exception as e:
            print(f"Insert failed, transaction rolled back: {e}")
            sys.exit(1)

        dates = sorted(r[3] for r in rows)
        print(f"Inserted {len(rows)} expenses for user_id={user_id}.")
        print(f"Date range: {dates[0]} to {dates[-1]}")
        print("Sample of 5 inserted records:")
        sample = conn.execute(
            "SELECT id, user_id, amount, category, date, description "
            "FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,),
        ).fetchall()
        for r in sample:
            print(f"  #{r['id']} | {r['date']} | {r['category']:13} | ₹{r['amount']:>8.2f} | {r['description']}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
