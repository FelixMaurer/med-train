# Allergieausweis Memory Trainer

A Streamlit app for training memorisation of "Allergieausweis" cards in batches
of 4 or 8, then testing recall and tracking progress over time. Built around the
*identify vs. reproduce* idea: faces, names and allergy lists are recognition
cues; dates, serials, blood groups, countries and the yes/no flag are the fields
you actually reproduce.

## What's in the box

```
allergie-trainer/
├── app.py            # the Streamlit app
├── generate_db.py    # one-time generator for the card database
├── cards.db          # 400 pre-generated cards (SQLite) — ready to use
├── requirements.txt
├── faces/            # YOU put face images here (see "Faces" below)
│   └── .gitkeep
├── .gitignore
└── README.md
```

## Quick start

```bash
pip install -r requirements.txt
# put your face PNGs into faces/ (optional — placeholders are used otherwise)
streamlit run app.py
```

`cards.db` already ships with 400 cards, so the app runs immediately.

## How it works

- **Draw a batch** (4 or 8) from the sidebar, then study the cards (rendered in
  the style of the original sheets).
- **Lückentest (recall):** the face and name are shown as cues; you fill in
  Geburtsdatum, Medikamenteneinnahme, Blutgruppe, Ausweisnummer and
  Ausstellungsland. Optionally also Name + Allergien (harder). Each field = 1
  point; a batch of 8 is scored out of 40.
- **Wissensquiz:** mixed aggregate + knowledge questions generated from the
  batch, e.g. *"how often does digit X appear across all serials?"*, *"how many
  take medication?"*, *"which allergy did NAME have?"*, *"who is this face?"*.
- **Score & progress:** every run is logged; the home page shows a score-over-
  time chart and a history table, plus average/best in the sidebar.

## Faces

Faces are **not** stored in the database. Each card holds a `face_index`. At
startup the app recursively scans `faces/` (including subfolders like
`faces/001/*.png`), sorts the file list deterministically, and resolves:

```
path = sorted_faces[face_index % len(sorted_faces)]
```

So every card stays bound to the same face for a given `faces/` folder, while
`cards.db` can be generated without the images present. Supported: `.png`,
`.jpg`, `.jpeg`. If `faces/` is empty, neutral gray placeholders are shown so
the app still works.

> **Note on 70k images + GitHub.** 70,000 PNGs will exceed normal GitHub repo
> limits and Streamlit Community Cloud storage. Options: (a) keep faces local
> and run the app on your machine; (b) use **Git LFS**; (c) host images
> externally and sync them into `faces/` at deploy time; or (d) commit only a
> subset (the modulo mapping handles any count). `.gitignore` excludes the face
> files by default.

## Saving / resuming

Streamlit Community Cloud has an ephemeral filesystem, so the robust way to
persist is the sidebar:

- **⬇️ Fortschritt herunterladen** — download a JSON of your history + active batch.
- **⬆️ Fortschritt laden** — upload it later to resume.

When running locally the app also auto-saves to `progress.json` for convenience.

## Regenerating the database

```bash
python generate_db.py              # 400 cards, seed 42 (default, reproducible)
python generate_db.py --n 800 --seed 7 --out cards.db
```

Faces (foods, medications, absurd objects), names (random letters incl. occasional
umlauts), Austrian "Jänner" for January, blood groups without rhesus (0 not O) —
all match the example sheets.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repo.
2. On share.streamlit.io, create an app pointing at `app.py`.
3. Provide `faces/` via one of the options above (or run without faces to test).
