import os
import json
import re
import subprocess
from datetime import datetime

posts_dir = "blogs/posts"
output_file = "blogs/posts.json"

posts = []

# Loop through all markdown files in the posts directory
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Extract Title (Finds the first line starting with #)
    title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace(".md", "")

    # 2. Extract Summary (Finds the first normal text paragraph)
    summary = ""
    paragraphs = content.split('\n\n')
    for p in paragraphs:
        clean_p = p.strip()
        # Skip headers, code blocks, and empty lines
        if clean_p and not clean_p.startswith('#') and not clean_p.startswith('```'):
            # Strip markdown characters like ** bolding
            summary = re.sub(r'[*_`]', '', clean_p)
            # Truncate if it's too long
            if len(summary) > 120:
                summary = summary[:117] + "..."
            break

    # 3. Extract Date (Reads the Git commit history for when the file was created)
    try:
        date_cmd = ['git', 'log', '--diff-filter=A', '--format=%ad', '--date=format:%b %Y', '--', filepath]
        git_date = subprocess.check_output(date_cmd).decode('utf-8').strip().lower()
        # Fallback to current date if not committed yet
        if not git_date:
            git_date = datetime.now().strftime("%b %Y").lower()
        else:
            git_date = git_date.split('\n')[-1] # Get earliest date
    except Exception:
        git_date = datetime.now().strftime("%b %Y").lower()

    post_id = filename.replace(".md", "")

    posts.append({
        "id": post_id,
        "title": title,
        "date": git_date,
        "file": filename,
        "summary": summary
    })

# Sort posts so the newest IDs are at the top (assumes you name them 1.md, 2.md, 3.md...)
posts.sort(key=lambda x: int(x["id"]) if x["id"].isdigit() else x["id"], reverse=True)

# Write the auto-generated JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=4)

print(f"Successfully generated {output_file} with {len(posts)} posts.")