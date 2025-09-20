
import os
import sqlite3
from typing import List, Dict, Any

def init_db(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        );
    """)
    conn.commit()
    conn.close()

def _conn():
    return sqlite3.connect(os.path.join("data", "startups.db"))

def add_startup(name: str, description: str) -> int:
    conn = _conn()
    c = conn.cursor()
    c.execute("INSERT INTO startups (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid

def list_startups() -> List[Dict[str, Any]]:
    conn = _conn()
    c = conn.cursor()
    rows = c.execute("SELECT id, name FROM startups ORDER BY id DESC").fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def get_startup(sid: int) -> Dict[str, Any]:
    conn = _conn()
    c = conn.cursor()
    row = c.execute("SELECT id, name, description FROM startups WHERE id=?", (sid,)).fetchone()
    conn.close()
    if not row:
        return {}
    return {"id": row[0], "name": row[1], "description": row[2]}

def search_startups(q: str) -> List[Dict[str, Any]]:
    conn = _conn()
    c = conn.cursor()
    like = f"%{q}%"
    rows = c.execute("SELECT id, name FROM startups WHERE name LIKE ? OR description LIKE ? LIMIT 50", (like, like)).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]
