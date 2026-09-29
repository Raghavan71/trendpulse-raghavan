"""
task3_analysis.py
TrendPulse - Task 3: load the clean CSV from Task 2, analyse it with
Pandas and NumPy, add two new columns, and save data/trends_analysed.csv.
"""

import os

import numpy as np
import pandas as pd

INPUT_FILE = os.path.join("data", "trends_clean.csv")
OUTPUT_FILE = os.path.join("data", "trends_analysed.csv")


def main():
    # ---------- Task 1: load and explore ----------
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found. Run task2_data_processing.py first.")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded data: {df.shape}\n")

    print("First 5 rows:")
    print(df.head(), "\n")

    # Pandas averages over every story
    print(f"Average score   : {df['score'].mean():,.0f}")
    print(f"Average comments: {df['num_comments'].mean():,.0f}\n")

    # ---------- Task 2: basic analysis with NumPy ----------
    # Convert the columns to NumPy arrays so np functions work on them directly
    scores = df["score"].to_numpy()

    print("--- NumPy Stats ---")
    print(f"Mean score   : {np.mean(scores):,.0f}")
    print(f"Median score : {np.median(scores):,.0f}")
    print(f"Std deviation: {np.std(scores):,.0f}")
    print(f"Max score    : {np.max(scores):,}")
    print(f"Min score    : {np.min(scores):,}\n")

    # Category with the most stories: value_counts sorts highest first
    category_counts = df["category"].value_counts()
    top_category = category_counts.index[0]
    print(f"Most stories in: {top_category} ({category_counts.iloc[0]} stories)\n")

    # Most commented story: np.argmax gives the row position of the largest value
    comments = df["num_comments"].to_numpy()
    top_row = np.argmax(comments)
    print(f"Most commented story: \"{df['title'].iloc[top_row]}\" "
          f"- {comments[top_row]:,} comments\n")

    # ---------- Task 3: add new columns ----------
    # engagement = discussion per upvote. The +1 avoids dividing by zero
    # if a story ever has a score of 0.
    df["engagement"] = df["num_comments"] / (df["score"] + 1)

    # is_popular = True when the score is above the average score
    average_score = df["score"].mean()
    df["is_popular"] = df["score"] > average_score

    # ---------- Task 4: save the result ----------
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()