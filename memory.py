import sqlite3
import os
import re
from contextlib import closing
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_memory.db")


def _run(sql, params=(), fetch=False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows if fetch else cur.rowcount


def init_db():
    _run("""CREATE TABLE IF NOT EXISTS facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        created TEXT NOT NULL)""")
    _run("""CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created TEXT NOT NULL)""")


def now():
    return datetime.now().isoformat(timespec="seconds")


# ---------- facts ----------
def remember_fact(text: str) -> str:
    text = text.strip(" .,!?")
    existing = [f.lower() for f in list_facts()]
    if text.lower() in existing:
        return "I already know that."
    _run("INSERT INTO facts (text, created) VALUES (?, ?)", (text, now()))
    return f"Got it. I'll remember that {text}."


def list_facts():
    rows = _run("SELECT text FROM facts ORDER BY id", fetch=True)
    return [r[0] for r in rows]


def forget_fact(keyword: str) -> str:
    n = _run("DELETE FROM facts WHERE text LIKE ?", (f"%{keyword}%",))
    return f"Okay, I forgot {n} thing{'s' if n != 1 else ''}." if n else "I didn't have anything like that saved."


def forget_all() -> str:
    _run("DELETE FROM facts")
    _run("DELETE FROM chat")
    return "Done. My memory is cleared."


# ---------- conversation history ----------
def save_message(role: str, content: str):
    _run("INSERT INTO chat (role, content, created) VALUES (?, ?, ?)", (role, content, now()))


def recent_messages(n: int = 10):
    rows = _run("SELECT role, content FROM chat ORDER BY id DESC LIMIT ?", (n,), fetch=True)
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def collapse_spelled_letters(text: str) -> str:
    # "R A H U L" or "R. A. H. U. L." -> "Rahul"
    def join(m):
        letters = re.findall(r"[A-Za-z]", m.group(0))
        return "".join(letters).capitalize()
    return re.sub(r"\b(?:[A-Za-z][\s.\-]+){2,}[A-Za-z]\b", join, text)
# ---------- voice commands ----------
def handle_memory_command(command: str):
    """Returns a spoken reply if this was a memory command, otherwise None."""
    text = command.strip().strip(" .,!?")
    low = text.lower()

    if re.search(r"what (do|did) you (remember|know) about me|what do you remember|list (my )?memories", low):
        facts = list_facts()
        if not facts:
            return "I don't have anything saved yet."
        return "Here's what I remember. " + ". ".join(facts) + "."

    if re.match(r"forget (everything|all)", low):
        return forget_all()

    m = re.match(r"forget (?:about |that )?(.+)", low)
    if m:
        return forget_fact(m.group(1))

    m = re.match(r"remember[,\s]+(?:that\s+)?(.+)", text, re.IGNORECASE)
    if m:
        return remember_fact(collapse_spelled_letters(m.group(1)))
    return None


init_db()