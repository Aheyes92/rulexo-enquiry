import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "schema.sql")
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "enquiry.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)


_SEED_CLIENT = {
    "id":            1,
    "name":          "Adam",
    "trade_type":    "AI automation systems for UK trade businesses",
    "email":         "aheyes1992@gmail.com",
    "phone":         None,
    "voice_profile": (
        "Direct, knowledgeable, no hype, human. Short sentences. No fluff. Say what you mean. "
        "Speak like someone who works in the trade. Never oversell - let results do the talking. "
        "Warm and relatable. Never corporate, never cold. Written for people who work with their hands."
    ),
}


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    tables = [
        row[0] for row in
        conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    ]
    for t in tables:
        print(f"  [OK] Table ready: {t}")
    conn.close()
    print(f"\nDatabase ready at: {DB_PATH}")


def seed_clients():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO clients (id, name, trade_type, email, phone, voice_profile)
            VALUES (:id, :name, :trade_type, :email, :phone, :voice_profile)
            """,
            _SEED_CLIENT,
        )
        conn.commit()
        if conn.execute("SELECT changes()").fetchone()[0]:
            print(f"  [SEEDED] client id=1 ({_SEED_CLIENT['name']})")
        else:
            print(f"  [SKIP] client id=1 already exists")
    finally:
        conn.close()


if __name__ == "__main__":
    print("Initialising Rulexo enquiry database...")
    init_db()
    print("\nSeeding clients...")
    seed_clients()
