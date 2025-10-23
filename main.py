import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

# ==== CONFIG ====
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # export GITHUB_TOKEN=xxxx
OWNER = "trustwallet"
REPO = "mobile-monorepo"
PER_PAGE = 50
DAYS_BACK = 7  # last 7 days

WHITELIST = [
    "orcchg",
    "ardmn",
    "jukov",
    "vcoolish",
    "DmitriySarafanoff",
    "eakurnikov",
    "reportedsocks",
    "Elyniss",
    "tonycode",
    "bulatgaleev",
    "rusmonster",
    "rebeccahsieh-oss",
    "Buddypas",
]

headers = {"Authorization": f"token {GITHUB_TOKEN}"}
cutoff_date = datetime.utcnow() - timedelta(days=DAYS_BACK)
cutoff_str = cutoff_date.strftime("%Y-%m-%d")

# --- API helpers ---
def search_prs():
    prs = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/search/issues"
            f"?q=repo:{OWNER}/{REPO}+is:pr+updated:>={cutoff_str}"
            f"&per_page={PER_PAGE}&page={page}"
        )
        r = requests.get(url, headers=headers)
        data = r.json()
        if "items" not in data or not data["items"]:
            break
        prs.extend(data["items"])
        page += 1
    return prs

def get_reviews(pr_number):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews"
    r = requests.get(url, headers=headers)
    return r.json()

def get_review_comments(pr_number):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}/comments"
    r = requests.get(url, headers=headers)
    return r.json()

def iso_to_dt(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

# --- Collect data ---
rows = []

prs = search_prs()
for pr in prs:
    pr_number = pr["number"]
    created_at = iso_to_dt(pr["created_at"])

    # Review events (approve / request changes / comment)
    for r in get_reviews(pr_number):
        if not r.get("submitted_at"):
            continue
        submitted_at = iso_to_dt(r["submitted_at"])
        if submitted_at < cutoff_date:
            continue
        if r["user"]["login"] not in WHITELIST:
            continue
        rows.append({
            "pr_number": pr_number,
            "reviewer": r["user"]["login"],
            "type": "review_event",
            "submitted_at": submitted_at,
            "time_to_first_review": (submitted_at - created_at).total_seconds() / 3600,
            "has_message": 1 if r.get("body") else 0,
        })

    # Inline code review comments
    for c in get_review_comments(pr_number):
        submitted_at = iso_to_dt(c["created_at"])
        if submitted_at < cutoff_date:
            continue
        if c["user"]["login"] not in WHITELIST:
            continue
        rows.append({
            "pr_number": pr_number,
            "reviewer": c["user"]["login"],
            "type": "inline_comment",
            "submitted_at": submitted_at,
            "time_to_first_review": (submitted_at - created_at).total_seconds() / 3600,
            "has_message": 1,
        })

df = pd.DataFrame(rows)

if df.empty:
    print("No reviews found in the last 7 days.")
    exit(0)

# --- Leaderboard ---
leaderboard = df.groupby("reviewer").agg(
    reviews_done=('type', lambda x: (x == "review_event").sum()),
    inline_comments=('type', lambda x: (x == "inline_comment").sum()),
    avg_time_to_first_review=('time_to_first_review', 'mean'),
    messages_written=('has_message', 'sum'),
).reset_index()

# Ensure numeric columns
for col in ["reviews_done","inline_comments","messages_written"]:
    if col not in leaderboard:
        leaderboard[col] = 0

leaderboard["total_activity"] = leaderboard["reviews_done"] + leaderboard["inline_comments"]

print("\n=== Weekly PR Review Leaderboard ===")
print(leaderboard.sort_values("total_activity", ascending=False))

# --- Plot 1: Reviews per Engineer ---
plt.figure(figsize=(10,6))
bars = plt.bar(leaderboard["reviewer"], leaderboard["reviews_done"], color="skyblue")
plt.title("Weekly PR Reviews per Engineer", fontsize=16)
plt.xlabel("Reviewer")
plt.ylabel("Number of Reviews")
plt.xticks(rotation=90)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha="center")
plt.tight_layout()
plt.savefig("weekly_reviews.png")
plt.show()

# --- Plot 2: Avg Time to First Review ---
plt.figure(figsize=(10,6))
plt.bar(leaderboard["reviewer"], leaderboard["avg_time_to_first_review"], color="orange")
plt.title("Average Time to First Review (hours)", fontsize=16)
plt.xlabel("Reviewer")
plt.ylabel("Hours")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("avg_review_time.png")
plt.show()

# --- Plot 3: Messages Written ---
plt.figure(figsize=(10,6))
bars = plt.bar(leaderboard["reviewer"], leaderboard["messages_written"], color="green")
plt.title("Weekly Review Messages per Engineer", fontsize=16)
plt.xlabel("Reviewer")
plt.ylabel("Messages Left")
plt.xticks(rotation=90)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha="center")
plt.tight_layout()
plt.savefig("review_messages.png")
plt.show()

# --- Plot 4: Combined Reviews + Inline Comments ---
plt.figure(figsize=(12,6))
x = range(len(leaderboard))
plt.bar(x, leaderboard["reviews_done"], width=0.4, label="Reviews (approve/request/comment)")
plt.bar([i+0.4 for i in x], leaderboard["inline_comments"], width=0.4, label="Inline Code Comments")
plt.xticks([i+0.2 for i in x], leaderboard["reviewer"], rotation=90)
plt.title("Weekly PR Review Activity per Engineer", fontsize=16)
plt.xlabel("Reviewer")
plt.ylabel("Count")
plt.legend()
plt.tight_layout()
plt.savefig("weekly_review_activity.png")
plt.show()

if not df.empty:
    repo_avg_time_to_first_review = df['time_to_first_review'].mean()
    print("\n=== Repository Average Metrics Weekly ===")
    print(f"Average Time to First Review: {repo_avg_time_to_first_review:.2f} hours")
    if not leaderboard.empty:
        repo_avg_reviews = leaderboard['reviews_done'].mean()
        repo_avg_comments = leaderboard['inline_comments'].mean()
        repo_avg_messages = leaderboard['messages_written'].mean()
        print(f"Average Reviews Done per Engineer: {repo_avg_reviews:.2f}")
        print(f"Average Inline Comments per Engineer: {repo_avg_comments:.2f}")
        print(f"Average Messages Written per Engineer: {repo_avg_messages:.2f}")