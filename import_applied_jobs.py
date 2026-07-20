import sqlite3
import pandas as pd

# ---------------------------------------------------
# FILE PATHS
# ---------------------------------------------------

EXCEL_FILE = r"C:\Users\yasho\Desktop\Job_Automation_Project\Application_Tracker.xlsx"

DATABASE = r"C:\Users\yasho\Desktop\Job_Automation_Project\jobs.db"

# ---------------------------------------------------

print("Reading Excel...")

df = pd.read_excel(EXCEL_FILE)

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

updated = 0
not_found = 0

for _, row in df.iterrows():

    company = str(row["Company Name"]).strip()
    title = str(row["Job Title"]).strip()

    cursor.execute("""
        UPDATE jobs
        SET status='APPLIED'
        WHERE
            LOWER(TRIM(company)) = LOWER(TRIM(?))
        AND LOWER(TRIM(title)) = LOWER(TRIM(?))
    """, (company, title))

    if cursor.rowcount:
        updated += cursor.rowcount
    else:
        not_found += 1

conn.commit()
conn.close()

print()
print("=" * 50)
print("Finished")
print("=" * 50)
print(f"Jobs updated : {updated}")
print(f"No match     : {not_found}")