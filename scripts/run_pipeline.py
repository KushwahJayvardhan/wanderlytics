"""
run_pipeline.py

Runs the full data pipeline end to end:
  1. Scrape Wikivoyage destination pages
  2. Clean the raw data with Pandas
  3. Load/upsert into the database

Usage:
    python scripts/run_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(cmd: list[str]):
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == "__main__":
    run([sys.executable, "scraper/scrape_wikivoyage.py"])
    run([sys.executable, "scraper/clean_data.py"])
    run([sys.executable, "-m", "database.seed"])
    print("\nPipeline complete.")
