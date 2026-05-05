import random
from datetime import datetime

from werkzeug.security import generate_password_hash

from database.db import get_db, init_db


FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Rahul", "Karan", "Siddharth", "Yash", "Aniket",
    "Aditi", "Ananya", "Diya", "Isha", "Kavya", "Meera", "Neha", "Priya",
    "Riya", "Sneha", "Pooja", "Anjali", "Shreya", "Divya", "Nisha",
    "Rajesh", "Suresh", "Ramesh", "Vikram", "Sanjay", "Manish", "Amit",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Shah", "Mehta",
    "Joshi", "Iyer", "Nair", "Menon", "Reddy", "Rao", "Naidu", "Pillai",
    "Chopra", "Kapoor", "Malhotra", "Bhatia", "Agarwal", "Mishra", "Pandey",
    "Tiwari", "Yadav", "Jain", "Desai", "Bose", "Chatterjee", "Mukherjee",
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]


def email_exists(conn, email):
    row = conn.execute(
        "SELECT 1 FROM users WHERE email = ?", (email,)
    ).fetchone()
    return row is not None


def generate_user(conn):
    while True:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        suffix = random.randint(10, 999)
        domain = random.choice(DOMAINS)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{suffix}@{domain}"
        if not email_exists(conn, email):
            return name, email


def main():
    init_db()
    conn = get_db()
    try:
        with conn:
            name, email = generate_user(conn)
            password_hash = generate_password_hash("password123")
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (name, email, password_hash, created_at),
            )
            user_id = cur.lastrowid

        print(f"id:    {user_id}")
        print(f"name:  {name}")
        print(f"email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
