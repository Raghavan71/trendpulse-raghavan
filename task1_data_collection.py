"""
task1_data_collection.py
TrendPulse - Task 1: fetch trending HackerNews stories, categorise them
by title keywords, and save them to a dated JSON file.
"""

import json
import os
import time
from datetime import datetime

import requests

# ---------- Configuration ----------
BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"User-Agent": "TrendPulse/1.0"}   # required header from the spec
MAX_IDS = 500                                # only look at the first 500 story IDs
PER_CATEGORY = 25                            # up to 25 stories per category (125 total)

# Categories are processed in this order. A story is given to the first
# category (that still has room) whose keywords appear in its title.
# Note: "show" also matches every "Show HN" post, which inflates entertainment.
CATEGORIES = {
    "technology":    ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"],
}

# Cache so each story is fetched from the API only once,
# even though we scan the ID list once per category.
story_cache = {}


def get_json(url):
    """GET a URL and return parsed JSON, or None if anything goes wrong."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()          # turns 4xx/5xx into exceptions
        return response.json()
    except requests.RequestException as e:
        # Don't crash the script - print and move on, as the task requires
        print(f"Request failed for {url}: {e}")
        return None


def get_story(story_id):
    """Fetch one story's details (cached)."""
    if story_id not in story_cache:
        story_cache[story_id] = get_json(f"{BASE_URL}/item/{story_id}.json")
    return story_cache[story_id]


def matches(title, keywords):
    """True if the title contains any keyword (case-insensitive substring match)."""
    title = title.lower()
    return any(kw.lower() in title for kw in keywords)


def main():
    # Step 1: get the list of top story IDs and keep the first 500
    story_ids = get_json(f"{BASE_URL}/topstories.json")
    if not story_ids:
        print("Could not fetch top stories. Exiting.")
        return
    story_ids = story_ids[:MAX_IDS]

    # Extra pool: sports/science have few matches, so also search HN's
    # "best stories" list (skipping IDs we already have).
    best_ids = get_json(f"{BASE_URL}/beststories.json") or []
    seen = set(story_ids)
    story_ids += [i for i in best_ids[:MAX_IDS] if i not in seen]

    collected = []
    used_ids = set()   # stories already assigned, so no story is counted twice
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 2: one pass per category
    for category, keywords in CATEGORIES.items():
        count = 0
        for story_id in story_ids:
            if count >= PER_CATEGORY:
                break                        # this category is full

            story = get_story(story_id)
            # Skip failed requests, deleted items, and items without a title
            if not story or "title" not in story:
                continue

            # Skip stories already used, or that don't match this category's keywords
            if story_id in used_ids or not matches(story["title"], keywords):
                continue
            used_ids.add(story_id)

            collected.append({
                "post_id": story["id"],
                "title": story["title"],
                "category": category,
                "score": story.get("score", 0),              # .get: field may be missing
                "num_comments": story.get("descendants", 0),
                "author": story.get("by", "unknown"),
                "collected_at": collected_at,
            })
            count += 1

        print(f"{category}: {count} stories")
        time.sleep(2)                        # ONE sleep per category loop, not per story

    # Step 3: save to data/trends_YYYYMMDD.json
    os.makedirs("data", exist_ok=True)       # create folder only if missing
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    print(f"Collected {len(collected)} stories. Saved to {filename}")


if __name__ == "__main__":
    main()