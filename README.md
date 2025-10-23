## Weekly PR Review Metrics

A Python script to track and visualize GitHub pull request (PR) review activity in your repository. It collects data for the last week and generates plots to monitor review count, review time, messages, and inline code comments per engineer.

⸻

Features
•	Fetches PRs updated in the last week using GitHub API.
•	Tracks per-engineer metrics:
•	Total PR reviews (approvals / request changes / comment reviews)
•	Inline code review comments
•	Average time to first review
•	Number of review messages
•	Generates four plots:
1.	Weekly PR reviews per engineer (weekly_reviews.png)
2.	Average time to first review (avg_review_time.png)
3.	Messages left during review (review_messages.png)
4.	Combined reviews and inline comments (weekly_review_activity.png)

⸻

### Prerequisites
•	Python 3.8+
•	GitHub Personal Access Token with repo scope
•	Python packages:

```pip install requests pandas matplotlib```



⸻

### Setup
1.	Clone the repository:
```
git clone https://github.com/your-org/weekly-pr-review-metrics.git
cd weekly-pr-review-metrics
```

	2.	Set your GitHub token as an environment variable:

```export GITHUB_TOKEN=your_personal_access_token```


	3.	Update configuration in the script if needed:

OWNER = "your-org-or-user"
REPO = "your-repo"
DAYS_BACK = 7  # number of days to include



⸻

### Usage

Run the script:

```python weekly_pr_review_metrics.py```

	•	The script will fetch PRs updated in the last DAYS_BACK days.
	•	Generate metrics and save plots as PNG files in the current directory.
	•	Prints a leaderboard in the console showing each reviewer’s activity.

⸻

### Output
1.	weekly_reviews.png – Number of PR reviews per engineer
2.	avg_review_time.png – Average time to first review (hours)
3.	review_messages.png – Review messages per engineer
4.	weekly_review_activity.png – Combined grouped bar chart of reviews vs inline comments

⸻

### Notes
•	Inline comments (/pulls/{pr}/comments) are included in the combined activity.
•	Only PRs updated within the last DAYS_BACK days are included.
•	Names on the X-axis are rotated vertically for readability.