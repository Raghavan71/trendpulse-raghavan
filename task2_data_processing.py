"""
task2_data_processing.py
TrendPulse - Task 2: load the JSON from Task 1 with Pandas, clean it,
and save it as data/trends_clean.csv.
"""

import glob
import os

import pandas as pd

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "trends_clean.csv")
MIN_SCORE = 5   # stories with a lower score are treated as low quality


def main():
    # ---------- Task 1: load the JSON file ----------
    # Task 1 names its file trends_YYYYMMDD.json. Sorting the names puts the
    # newest date last (YYYYMMDD sorts correctly as text), so [-1] is the latest.
    files = sorted(glob.glob(os.path.join(DATA_DIR, "trends_2*.json")))
    if not files:
        print("No trends_*.json file found in data/. Run Task 1 first.")
        return
    json_path = files[-1]

    df = pd.read_json(json_path)
    print(f"Loaded {len(df)} stories from {json_path}\n")

    # ---------- Task 2: clean the data ----------
    # 1. Whitespace: strip extra spaces from titles first, so a title that is
    #    only spaces becomes empty and is caught by the missing-value step.
    df["title"] = df["title"].astype(str).str.strip()
    df["title"] = df["title"].replace("", pd.NA)

    # 2. Duplicates: the same post_id must appear only once.
    df = df.drop_duplicates(subset="post_id")
    print(f"After removing duplicates: {len(df)}")

    # 3. Missing values: drop rows missing post_id, title or score.
    #    to_numeric with errors="coerce" turns unreadable scores into NaN,
    #    so they are dropped here too.
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # 4. Data types: score and num_comments must be integers.
    #    Missing comment counts are treated as 0 so the int conversion works.
    df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0)
    df["score"] = df["score"].astype(int)
    df["num_comments"] = df["num_comments"].astype(int)

    # 5. Low quality: keep only stories with a score of at least 5.
    df = df[df["score"] >= MIN_SCORE]
    print(f"After removing low scores: {len(df)}\n")

    # ---------- Task 3: save as CSV and print summary ----------
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}\n")

    print("Stories per category:")
    counts = df["category"].value_counts()
    for category, count in counts.items():
        print(f"  {category:<14}{count}")


if __name__ == "__main__":
    main()