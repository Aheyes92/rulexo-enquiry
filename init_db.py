import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "schema.sql")
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "enquiry.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)


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


if __name__ == "__main__":
    print("Initialising Rulexo enquiry database...")
    init_db()
