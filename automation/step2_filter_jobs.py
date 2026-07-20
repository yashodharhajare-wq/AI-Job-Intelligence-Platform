import sqlite3
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
DB_FILE = "jobs.db"
KEYWORD_FILE = Path("config") / "excluded_keywords.txt"


# -----------------------------
# Load keywords
# -----------------------------
def load_keywords():
    keywords = []

    with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()

            if not line:
                continue

            if line.startswith("#"):
                continue

            keywords.append(line)

    return keywords


# -----------------------------
# Find matching keyword
# -----------------------------
def find_match(title, keywords):

    title = title.lower()

    for keyword in keywords:

        if keyword in title:
            return keyword

    return None


# -----------------------------
# Main
# -----------------------------
def main():

    keywords = load_keywords()

    print(f"{len(keywords)} keywords loaded.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM jobs
        WHERE status IS NULL
        OR status = ''
        OR status = 'NEW'
    """)


    jobs = cursor.fetchall()

    updated = 0
    excluded_jobs = []

    for job_id, title in jobs:

        if not title:
            continue

        match = find_match(title, keywords)

        if match:

           reason = f"Matched keyword: {match}"

           cursor.execute("""
                UPDATE jobs
                SET status = ?,
                    reason = ?
                WHERE id = ?
            """, (
                "EXCLUDED",
                reason,
                job_id
            ))

           excluded_jobs.append((title, reason))

           updated += 1

    conn.commit()
    conn.close()

    print("\n--------------------------------")
    print(f"Jobs checked : {len(jobs)}")
    print(f"Jobs excluded: {updated}")
    print("--------------------------------")

    if excluded_jobs:

        print("\nExcluded Jobs\n")

        for title, reason in excluded_jobs:

            print(f"• {title}")
            print(f"  {reason}")
            print()

    else:

        print("\nNo jobs were excluded.")


if __name__ == "__main__":
    main()