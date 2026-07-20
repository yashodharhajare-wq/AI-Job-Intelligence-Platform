import sqlite3

DB_FILE = "jobs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Existing database upgrade
columns = {
    "status": "TEXT DEFAULT 'NEW'",
    "reason": "TEXT",
    "notes": "TEXT",
    "first_seen": "TEXT",
    "last_seen": "TEXT"
}

# Get existing columns
cursor.execute("PRAGMA table_info(jobs)")
existing_columns = [row[1] for row in cursor.fetchall()]

for column, definition in columns.items():
    if column not in existing_columns:
        print(f"Adding column: {column}")
        cursor.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

# Initialize existing records
cursor.execute("""
UPDATE jobs
SET
    status = COALESCE(status, 'NEW'),
    first_seen = COALESCE(first_seen, scraped_at),
    last_seen = COALESCE(last_seen, scraped_at)
""")

conn.commit()
conn.close()

print("Database updated successfully.")