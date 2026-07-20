import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox
from urllib.parse import quote
from playwright.sync_api import sync_playwright

from config import PROFILE_PATH

DEBUG = False
DATABASE_NAME = "jobs.db"


# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------

def initialize_database():

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,
            company TEXT,
            location TEXT,

            link TEXT UNIQUE,

            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_job(job):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""

        INSERT OR IGNORE INTO jobs
        (
            title,
            company,
            location,
            link
        )

        VALUES
        (?, ?, ?, ?)

    """,
    (
        job["title"],
        job["company"],
        job["location"],
        job["link"]
    ))

    inserted = cursor.rowcount

    conn.commit()
    conn.close()

    return inserted == 1


# ----------------------------------------------------
# TKINTER
# ----------------------------------------------------

def get_scrape_settings():

    root = tk.Tk()
    root.withdraw()

    search_title = simpledialog.askstring(
        "Stepstone Scraper",
        "Search Title:",
        initialvalue="Project Manager"
    )

    if not search_title:
        return None, None, None

    start_page = simpledialog.askinteger(
        "Stepstone Scraper",
        "Start Page:",
        initialvalue=1,
        minvalue=1
    )

    if start_page is None:
        return None, None, None

    end_page = simpledialog.askinteger(
        "Stepstone Scraper",
        "End Page:",
        initialvalue=start_page,
        minvalue=start_page
    )

    if end_page is None:
        return None, None, None

    root.destroy()

    return search_title, start_page, end_page

# ----------------------------------------------------
# URL
# ----------------------------------------------------

def build_page_url(search_title, page_number):

    search = quote(search_title.lower().replace(" ", "-"))

    return (
        f"https://www.stepstone.de/jobs/{search}"
        f"?page={page_number}"
        f"&sort=2"
        f"&action=sort_publish"
        f"&searchOrigin=membersarea"
    )
# ----------------------------------------------------
# SCRAPER
# ----------------------------------------------------

def scrape_jobs(search_title, start_page, end_page):

    total_jobs = 0
    new_jobs = 0
    duplicate_jobs = 0

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            channel="chrome",
            headless=False
        )

        page = context.pages[0] if context.pages else context.new_page()

        for current_page in range(start_page, end_page + 1):

            print("\n" + "=" * 60)
            print(f"SCRAPING PAGE {current_page}")
            print("=" * 60)

            url = build_page_url(search_title, current_page)

            page.goto(
                url,
                wait_until="networkidle"
            )

            # Remove recommendation widget if present
            recommender = page.locator(
                '[id^="recommender-widget-content"]'
            )

            if recommender.count() > 0:
                recommender.evaluate("el => el.remove()")

            all_jobs = page.locator(
                '[data-testid="job-item"]'
            )

            job_count = all_jobs.count()

            print(f"Found {job_count} jobs")

            if job_count == 0:
                print("No jobs found on this page.")
                continue

            for i in range(job_count):

                try:

                    job = all_jobs.nth(i)

                    title = job.locator(
                        '[data-testid="job-item-title"]'
                    ).inner_text().strip()

                    company = job.locator(
                        '[data-at="job-item-company-name"]'
                    ).inner_text().strip()

                    location = job.locator(
                        '[data-at="job-item-location"]'
                    ).inner_text().strip()

                    link = job.locator(
                        '[data-testid="job-item-title"]'
                    ).get_attribute("href")

                    if link and link.startswith("/"):
                        link = "https://www.stepstone.de" + link

                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": link
                    }

                    inserted = save_job(job_data)

                    total_jobs += 1

                    if inserted:

                        new_jobs += 1

                        print(
                            f"[NEW] {title} | {company}"
                        )

                    else:

                        duplicate_jobs += 1

                        print(
                            f"[DUPLICATE] {title}"
                        )

                except Exception as e:

                    print(
                        f"Skipped one job because of error:\n{e}\n"
                    )

        context.close()

    return {
        "total": total_jobs,
        "new": new_jobs,
        "duplicates": duplicate_jobs
    }
# ----------------------------------------------------
# MAIN
# ----------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("STEPSTONE SCRAPER")
    print("=" * 60)

    initialize_database()

    search_title, start_page, end_page = get_scrape_settings()

    if start_page is None or end_page is None:

        print("Scraping cancelled.")

    else:

        print()
        print(f"Scraping pages {start_page} to {end_page}")
        print()

        stats = scrape_jobs(
            search_title,
            start_page,
            end_page
        )

        print()
        print("=" * 60)
        print("SCRAPING FINISHED")
        print("=" * 60)

        print(f"Pages scraped : {end_page - start_page + 1}")
        print(f"Jobs processed: {stats['total']}")
        print(f"New jobs      : {stats['new']}")
        print(f"Duplicates    : {stats['duplicates']}")

        print()
        print("Database saved as jobs.db")