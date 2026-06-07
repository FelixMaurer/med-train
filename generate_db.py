"""
generate_db.py
--------------
Generates the static card database (cards.db, SQLite) with N randomly
generated "Allergieausweis" cards in the style of the FOPRA example sheets.

Run once:   python generate_db.py
Re-run with a different count / seed:
            python generate_db.py --n 400 --seed 42

Faces are NOT baked into the DB. Each card stores a `face_index` (a large
integer). At runtime the app globs the faces/ folder (recursively), sorts the
file list deterministically, and resolves the image via
        path = faces_sorted[face_index % len(faces_sorted)]
This keeps every card bound to the same face for a given faces/ folder, while
letting the DB be generated without the images present.
"""

import argparse
import json
import random
import sqlite3
from pathlib import Path

# --- German month names (Austrian "Jänner" to match the example sheets) -----
MONTHS = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # no leap year

BLOOD = ["A", "B", "AB", "0"]  # no rhesus, German uses 0 (not O)

COUNTRIES = [
    "Frankreich", "Deutschland", "Italien", "Österreich", "China", "Spanien",
    "Portugal", "Schweiz", "Belgien", "Niederlande", "Polen", "Schweden",
    "Norwegen", "Dänemark", "Finnland", "Griechenland", "Türkei", "Japan",
    "Indien", "Brasilien", "Kanada", "Mexiko", "Argentinien", "Australien",
    "Ägypten", "Marokko", "Kroatien", "Ungarn", "Tschechien", "Irland",
    "Island", "Russland", "Ukraine", "Rumänien", "Slowenien", "Slowakei",
]

# Mix of real allergens, medications and absurd objects to match the sheets
# (Soja, Schnitzel, Batterien, Rituximab, Gold, Elfen, Geldscheine ...)
ALLERGIES = [
    # food / real allergens
    "Soja", "Schnitzel", "Pasta", "Tomaten", "Erdnüsse", "Milch", "Eier",
    "Weizen", "Pollen", "Hausstaub", "Katzenhaare", "Latex", "Nickel",
    "Sonnencreme", "Sauerstoff", "Schnee", "Burger",
    # medications
    "Penicillin", "Ibuprofen", "Aspirin", "Rituximab", "Cortison", "Insulin",
    # absurd objects
    "Batterien", "Ratten", "Gold", "Brillen", "Pflanzen", "Autos", "Elfen",
    "Geldscheine", "Steine", "Wolken", "Regen", "Bücher", "Telefone",
    "Schuhe", "Fenster", "Türen", "Kissen", "Lampen", "Stühle", "Wasser",
    "Feuer", "Musik", "Farben", "Spiegel", "Uhren", "Schlüssel", "Tische",
]

UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
UMLAUTS = ["Ä", "Ö", "Ü"]
FACE_POOL = 70000  # large index space; runtime takes modulo by real face count


def random_name(rng: random.Random) -> str:
    """Random uppercase 'name' of varying length, occasional umlaut, no spaces."""
    n = rng.randint(5, 8)
    chars = []
    for _ in range(n):
        if rng.random() < 0.05:
            chars.append(rng.choice(UMLAUTS))
        else:
            chars.append(rng.choice(UPPER))
    return "".join(chars)


def build_rows(n: int, rng: random.Random):
    face_indices = rng.sample(range(FACE_POOL), n)  # unique to minimise clashes
    rows = []
    for i in range(n):
        m = rng.randint(0, 11)
        day = rng.randint(1, DAYS_IN_MONTH[m])
        name = random_name(rng)
        takes = 1 if rng.random() < 0.5 else 0
        blood = rng.choice(BLOOD)
        allergies = rng.sample(ALLERGIES, rng.randint(3, 5))
        serial = str(rng.randint(10000, 99999))  # exactly 5 digits, no leading 0
        country = rng.choice(COUNTRIES)
        rows.append((
            i + 1, name, day, MONTHS[m], m + 1, takes, blood,
            json.dumps(allergies, ensure_ascii=False), serial, country,
            face_indices[i],
        ))
    return rows


def write_db(path: str, rows):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS cards")
    c.execute("""
        CREATE TABLE cards (
            id              INTEGER PRIMARY KEY,
            name            TEXT,
            birth_day       INTEGER,
            birth_month     TEXT,
            birth_month_num INTEGER,
            takes_medication INTEGER,   -- 0/1
            blood_group     TEXT,
            allergies       TEXT,       -- JSON list
            serial          TEXT,       -- 5-digit string
            country         TEXT,
            face_index      INTEGER
        )
    """)
    c.executemany(
        "INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400, help="number of cards")
    ap.add_argument("--seed", type=int, default=42, help="rng seed (reproducible)")
    ap.add_argument("--out", default="cards.db", help="output sqlite path")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows = build_rows(args.n, rng)
    write_db(args.out, rows)
    print(f"Wrote {len(rows)} cards to {Path(args.out).resolve()} (seed={args.seed})")


if __name__ == "__main__":
    main()
