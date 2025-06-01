import os
import subprocess
import requests
import json

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
BEFORE = os.getenv("GITHUB_EVENT_BEFORE")
AFTER = os.getenv("GITHUB_EVENT_AFTER")
REPO = os.getenv("GITHUB_REPOSITORY")

log_cmd = ["git", "log", f"{BEFORE}..{AFTER}", "--pretty=format:%s|%an|%cI|%H"]
result = subprocess.run(log_cmd, stdout=subprocess.PIPE)
commits = result.stdout.decode("utf-8").strip().split("\n")

for line in commits:
    if not line.strip():
        continue
    try:
        message, author, timestamp, commit_hash = line.split("|")
    except ValueError:
        continue  # 커밋 메시지에 |가 포함되어 있을 경우 방지

    commit_url = f"https://github.com/{REPO}/commit/{commit_hash}"

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "커밋 메시지": {"title": [{"text": {"content": message}}]},
            "작성자": {"rich_text": [{"text": {"content": author}}]},
            "날짜": {"date": {"start": timestamp}},
            "링크": {"url": commit_url}
        }
    }

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(payload))
    print(f"📌 {message} → {response.status_code}")
    print(f"Response JSON: {response.text}")
