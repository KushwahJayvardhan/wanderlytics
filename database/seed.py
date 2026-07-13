"""
seed.py

Loads scraper/raw_data/destinations_clean.csv into the database.
Uses upsert-by-name logic so re-running the pipeline updates existing
rows instead of creating duplicates.

Usage:
    python -m database.seed
"""

from pathlib import Path

import pandas as pd

from database.database import Base, SessionLocal, engine
from database.models import Destination

CSV_PATH = Path(__file__).parent.parent / "scraper" / "raw_data" / "destinations_clean.csv"


def run():
    Base.metadata.create_all(bind=engine)
    df = pd.read_csv(CSV_PATH)

    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            existing = db.query(Destination).filter_by(name=row["name"]).first()
            values = dict(
                name=row["name"],
                description=row["description"],
                short_description=row.get("short_description"),
                popularity_score=row.get("popularity_score", 0.0),
                latitude=row.get("latitude") if pd.notna(row.get("latitude")) else None,
                longitude=row.get("longitude") if pd.notna(row.get("longitude")) else None,
                source_url=row.get("source_url"),
            )
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                db.add(Destination(**values))
        db.commit()
        print(f"Seeded/updated {len(df)} destinations.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
