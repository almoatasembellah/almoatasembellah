"""Write the newest public repositories into the profile READMEs.

Replaces everything between <!-- RECENT-REPOS:START --> and <!-- RECENT-REPOS:END -->
in README.md and README.ar.md. Runs from .github/workflows/recent-repos.yml.
"""
import json
import os
import re
import urllib.request

USER = "almoatasembellah"
LIMIT = 6
FILES = ["README.md", "README.ar.md"]
SKIP = {USER.lower()}

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&direction=desc&per_page=50",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-updater"},
)
token = os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")
with urllib.request.urlopen(req, timeout=30) as r:
    repos = json.load(r)

repos = [x for x in repos if not x["fork"] and not x["archived"] and x["name"].lower() not in SKIP][:LIMIT]


def esc(text):
    return (text or "").replace("|", "\|").replace("\n", " ").strip()


rows = ["| Repository | About | Language | Last update |", "| --- | --- | --- | --- |"]
for x in repos:
    rows.append(
        f"| [{x['name']}]({x['html_url']}) | {esc(x['description']) or '—'} | "
        f"{x['language'] or '—'} | {x['pushed_at'][:10]} |"
    )
block = "<!-- RECENT-REPOS:START -->\n" + "\n".join(rows) + "\n<!-- RECENT-REPOS:END -->"

pattern = re.compile(r"<!-- RECENT-REPOS:START -->.*?<!-- RECENT-REPOS:END -->", re.S)
for name in FILES:
    with open(name, encoding="utf-8") as f:
        text = f.read()
    new = pattern.sub(block, text)
    if new != text:
        with open(name, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("updated", name)
