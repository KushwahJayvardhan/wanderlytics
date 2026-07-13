"""
clean_data.py

Reads the raw scraped JSON, cleans it with Pandas, and exports a
ready-to-load CSV.

Cleaning steps:
- Drop duplicates by destination name
- Drop rows missing required fields (name, description)
- Fill missing coordinates with None (kept, not dropped -- optional field)
- Standardize whitespace / strip HTML leftovers
- Feature engineering: a simple popularity_score placeholder based on
  how many "highlights" were found (stand-in until you wire up a
  real signal, e.g. page views via the Wikimedia API)
"""

import json
from pathlib import Path

import pandas as pd

RAW_PATH = Path(__file__).parent / "raw_data" / "destinations_raw.json"
CLEAN_CSV_PATH = Path(__file__).parent / "raw_data" / "destinations_clean.csv"


def load_raw() -> pd.DataFrame:
    data = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    return pd.DataFrame(data)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Standardize text fields
    df["name"] = df["name"].str.strip()
    df["description"] = df["description"].str.strip()

    # Required fields -- drop rows missing these
    df = df.dropna(subset=["name", "description"])
    df = df[df["description"].str.len() > 0]

    # Duplicates
    df = df.drop_duplicates(subset=["name"])

    # highlights is a list column -- store as a joined string for CSV,
    # keep count for feature engineering
    df["highlight_count"] = df["highlights"].apply(len)
    df["highlights_joined"] = df["highlights"].apply(lambda items: " | ".join(items))

    # Simple popularity score placeholder (0-100 scale)
    max_highlights = df["highlight_count"].max() or 1
    df["popularity_score"] = (df["highlight_count"] / max_highlights * 100).round(1)

    # Truncate very long descriptions for card display; keep full text separately
    df["short_description"] = df["description"].str.slice(0, 220)

    return df[
        [
            "name",
            "description",
            "short_description",
            "highlights_joined",
            "highlight_count",
            "popularity_score",
            "latitude",
            "longitude",
            "source_url",
        ]
    ]


if __name__ == "__main__":
    raw_df = load_raw()
    print(f"Loaded {len(raw_df)} raw records")

    clean_df = clean(raw_df)
    print(f"{len(clean_df)} records after cleaning")

    clean_df.to_csv(CLEAN_CSV_PATH, index=False)
    print(f"Saved cleaned data to {CLEAN_CSV_PATH}")
