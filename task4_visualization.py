"""
task4_visualization.py
TrendPulse - Task 4: load data/trends_analysed.csv, draw 3 Matplotlib charts
plus a combined dashboard, and save them as PNG files in outputs/.
"""

import os

import matplotlib
matplotlib.use("Agg")   # draw straight to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd

INPUT_FILE = os.path.join("data", "trends_analysed.csv")
OUTPUT_DIR = "outputs"

# One colour per category, reused so the same category looks the same everywhere
CATEGORY_COLOURS = {
    "technology": "#4C72B0",
    "worldnews": "#DD8452",
    "sports": "#55A868",
    "science": "#C44E52",
    "entertainment": "#8172B3",
}


def shorten(title, limit=50):
    """Cut titles longer than `limit` characters and add '...' at the end."""
    return title if len(title) <= limit else title[:limit - 3] + "..."


def chart_top_stories(df, ax):
    """Chart 1: horizontal bar chart of the 10 highest-scoring stories."""
    top10 = df.nlargest(10, "score")
    labels = [shorten(t) for t in top10["title"]]
    ax.barh(labels, top10["score"], color="#4C72B0")
    ax.invert_yaxis()                     # highest score at the top
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story title")


def chart_categories(df, ax):
    """Chart 2: bar chart of how many stories each category has."""
    counts = df["category"].value_counts()
    colours = [CATEGORY_COLOURS.get(c, "grey") for c in counts.index]
    ax.bar(counts.index, counts.values, color=colours)
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of stories")
    ax.tick_params(axis="x", rotation=30)


def chart_scatter(df, ax):
    """Chart 3: score vs comments, coloured by is_popular."""
    popular = df[df["is_popular"]]
    not_popular = df[~df["is_popular"]]
    ax.scatter(not_popular["score"], not_popular["num_comments"],
               color="#8C8C8C", alpha=0.7, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"],
               color="#C44E52", alpha=0.8, label="Popular")
    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Number of comments")
    ax.legend()


def save_single(draw_function, df, filename, size):
    """Draw one chart on its own figure and save it as a PNG."""
    fig, ax = plt.subplots(figsize=size)
    draw_function(df, ax)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=150)           # savefig BEFORE show, as the spec says
    plt.close(fig)
    print(f"Saved {path}")


def main():
    # ---------- Setup ----------
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found. Run task3_analysis.py first.")
        return

    df = pd.read_csv(INPUT_FILE)
    # A CSV stores True/False as text; make sure the column is a real boolean
    df["is_popular"] = df["is_popular"].astype(bool)
    os.makedirs(OUTPUT_DIR, exist_ok=True)   # create outputs/ only if missing
    print(f"Loaded {len(df)} stories from {INPUT_FILE}")

    # ---------- The 3 charts ----------
    save_single(chart_top_stories, df, "chart1_top_stories.png", (11, 6))
    save_single(chart_categories, df, "chart2_categories.png", (8, 5))
    save_single(chart_scatter, df, "chart3_scatter.png", (8, 6))

    # ---------- Bonus: combined dashboard ----------
    fig, axes = plt.subplots(1, 3, figsize=(22, 6))
    chart_top_stories(df, axes[0])
    chart_categories(df, axes[1])
    chart_scatter(df, axes[2])
    fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold")
    fig.tight_layout()
    dashboard_path = os.path.join(OUTPUT_DIR, "dashboard.png")
    fig.savefig(dashboard_path, dpi=150)
    plt.close(fig)
    print(f"Saved {dashboard_path}")


if __name__ == "__main__":
    main()