import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError

from config import PROFILE_PATH


# ==========================================================
# CONFIGURATION
# ==========================================================

DATABASE_NAME = "jobs.db"
RESUME_FILE = "resume.json"

HEADLESS = False

STEPSTONE_HOME = "https://www.stepstone.de/jobs"

DEBUG = False


# ==========================================================
# DATABASE
# ==========================================================

DATABASE_SCHEMA = """

CREATE TABLE IF NOT EXISTS jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    location TEXT,
    link TEXT UNIQUE,
    page INTEGER,
    search_title TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied INTEGER DEFAULT 0,
    ai_score REAL,
    ai_decision TEXT,
    notes TEXT
    status TEXT DEFAULT 'NEW',
    reason TEX
);
"""

def initialize_database():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    cursor.execute(DATABASE_SCHEMA)

    conn.commit()

    conn.close()


# ==========================================================
# LOGGER
# ==========================================================

def log(message):

    current = datetime.now().strftime("%H:%M:%S")

    print(f"[{current}] {message}")


# ==========================================================
# RESUME
# ==========================================================

def save_resume(search_title, current_page):

    data = {

        "search_title": search_title,

        "page": current_page

    }

    with open(RESUME_FILE, "w") as f:

        json.dump(data, f)


def load_resume():

    if not Path(RESUME_FILE).exists():

        return None

    with open(RESUME_FILE, "r") as f:

        return json.load(f)


def delete_resume():

    if Path(RESUME_FILE).exists():

        Path(RESUME_FILE).unlink()


# ==========================================================
# TIMER
# ==========================================================

def format_time(seconds):

    seconds = int(seconds)

    h = seconds // 3600

    m = (seconds % 3600) // 60

    s = seconds % 60

    return f"{h:02}:{m:02}:{s:02}"
# ==========================================================
# TKINTER GUI
# ==========================================================

def get_scrape_settings():

    resume_data = load_resume()

    result = {}

    window = tk.Tk()

    window.title("Stepstone Job Scraper")

    window.geometry("420x270")

    window.resizable(False, False)

    window.columnconfigure(1, weight=1)

    # -----------------------------
    # Search Title
    # -----------------------------

    tk.Label(
        window,
        text="Search Title:"
    ).grid(row=0, column=0, padx=10, pady=(15, 5), sticky="w")

    search_entry = ttk.Entry(window, width=35)

    search_entry.grid(
        row=0,
        column=1,
        padx=10,
        pady=(15, 5),
        sticky="ew"
    )

    search_entry.insert(0, "Project Manager")

    # -----------------------------
    # Start Page
    # -----------------------------

    tk.Label(
        window,
        text="Start Page:"
    ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

    start_entry = ttk.Entry(window, width=10)

    start_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    start_entry.insert(0, "1")

    # -----------------------------
    # End Page
    # -----------------------------

    tk.Label(
        window,
        text="End Page:"
    ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

    end_entry = ttk.Entry(window, width=10)

    end_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    end_entry.insert(0, "50")

    # -----------------------------
    # Resume checkbox
    # -----------------------------

    resume_var = tk.BooleanVar(value=False)

    if resume_data:

        resume_checkbox = ttk.Checkbutton(

            window,

            text=f"Resume previous scrape ({resume_data['search_title']} - Page {resume_data['page']})",

            variable=resume_var

        )

        resume_checkbox.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="w"
        )

    # -----------------------------
    # Start Button
    # -----------------------------

    def start():

        try:

            result["search_title"] = search_entry.get().strip()

            result["start_page"] = int(start_entry.get())

            result["end_page"] = int(end_entry.get())

            result["resume"] = resume_var.get()

            if result["search_title"] == "":

                messagebox.showerror(
                    "Error",
                    "Please enter a search title."
                )

                return

            if result["start_page"] < 1:

                messagebox.showerror(
                    "Error",
                    "Start page must be at least 1."
                )

                return

            if result["end_page"] < result["start_page"]:

                messagebox.showerror(
                    "Error",
                    "End page must be greater than or equal to Start page."
                )

                return

            window.destroy()

        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter valid page numbers."
            )

    ttk.Button(

        window,

        text="Start Scraping",

        command=start

    ).grid(
        row=5,
        column=0,
        columnspan=2,
        pady=20
    )

    search_entry.focus()

    window.mainloop()

    if not result:

        return None

    return result

# ==========================================================
# DATABASE FUNCTIONS
# ==========================================================

def open_database():

    conn = sqlite3.connect(DATABASE_NAME)

    cursor = conn.cursor()

    return conn, cursor


def close_database(conn):

    conn.commit()

    conn.close()


def save_job(cursor, job):

    cursor.execute("""

        INSERT OR IGNORE INTO jobs
        (

            title,

            company,

            location,

            link,

            page,

            search_title,

            status

        )

        VALUES

        (?, ?, ?, ?, ?, ?, ?)

    """,

    (

        job["title"],

        job["company"],

        job["location"],

        job["link"],

        job["page"],

        job["search_title"],

        "NEW"

    ))

    return cursor.rowcount == 1

    # ==========================================================
# PLAYWRIGHT FUNCTIONS
# ==========================================================

def launch_browser(playwright):

    log("Launching Chrome...")

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        channel="chrome",
        headless=HEADLESS
    )

    page = browser.new_page()

    return browser, page


def remove_recommendation_widget(page):

    try:

        widget = page.locator('[id^="recommender-widget-content"]')

        if widget.count() > 0:

            page.evaluate("""
                document
                    .querySelectorAll('[id^="recommender-widget-content"]')
                    .forEach(e => e.remove());
            """)

    except Exception:

        pass


def search_jobs(page, search_title):

    log(f"Searching for: {search_title}")

    page.goto(STEPSTONE_HOME, wait_until="domcontentloaded")

    page.wait_for_timeout(2000)

    # Reject cookie banner if present
    try:

        page.get_by_role("button", name="Accept").click(timeout=3000)

    except Exception:

        pass

    # Search field
    search_box = page.locator("input").first

    search_box.click()

    search_box.fill(search_title)

    search_box.press("Enter")

    page.wait_for_load_state("networkidle")

    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(page.url)

    params = parse_qs(parsed.query)

    params["sort"] = ["2"]
    params["action"] = ["sort_publish"]

    new_query = urlencode(params, doseq=True)

    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    log(f"Applying newest-first sorting...")
    page.goto(new_url, wait_until="networkidle")

    remove_recommendation_widget(page)


def open_results_page(page, page_number):

    from urllib.parse import (
        urlparse,
        parse_qs,
        urlencode,
        urlunparse
    )

    parsed = urlparse(page.url)

    params = parse_qs(parsed.query)

    params["page"] = [str(page_number)]

    new_query = urlencode(params, doseq=True)

    target = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    log(f"Opening page {page_number}")

    page.goto(target, wait_until="networkidle")

    remove_recommendation_widget(page)


def extract_jobs(page, current_page, search_title):

    jobs = []

    cards = page.locator('[data-testid="job-item"]')

    count = cards.count()

    log(f"Found {count} jobs")

    for i in range(count):
        print()
        log(f"Processing card {i+1}/{count}")

        card = cards.nth(i)

        try:

            title = ""

            company = ""

            location = ""

            link = ""

            # ------------------------
            # Title
            # ------------------------

            try:

        
                locator = card.locator('[data-testid="job-item-title"]')

                if locator.count():

                    title = locator.first.inner_text().strip()

                    log(f"Title: {title}")

            except Exception:
                pass

            # ------------------------
            # Company
            # ------------------------

            try:

                locator = card.locator('[data-at="job-item-company-name"] div')
                if locator.count():
                    company = locator.first.inner_text().strip()
                    log(f"Company: {company}")

            except Exception:
                pass

            # ------------------------
            # Location
            # ------------------------

            try:

                locator = card.locator('[data-at="job-item-location"]')

                if locator.count():

                    location = locator.first.inner_text().strip()

                    log(f"Location: {location}")

            except Exception:
                pass

            # ------------------------
            # Link
            # ------------------------

            try:

                # print("Reading link...")

                locator = card.locator('[data-testid="job-item-title"]')

                href = locator.get_attribute("href")

                if href:

                    if href.startswith("/"):

                        link = "https://www.stepstone.de" + href

                    else:

                        link = href

            except Exception:

                pass

            if not title:

                continue

            jobs.append({

                "title": title,

                "company": company,

                "location": location,

                "link": link,

                "page": current_page,

                "search_title": search_title

            })

        except Exception as e:

            log(f"Error reading job: {e}")

    return jobs

    # ==========================================================
# MAIN SCRAPER
# ==========================================================

def scrape_jobs(settings):

    search_title = settings["search_title"]
    start_page = settings["start_page"]
    end_page = settings["end_page"]

    # -------------------------
    # Resume previous scrape
    # -------------------------

    if settings.get("resume"):

        resume = load_resume()

        if resume:

            search_title = resume["search_title"]
            start_page = resume["page"]

            log(f"Resuming '{search_title}' from page {start_page}")

    initialize_database()

    conn, cursor = open_database()

    total_jobs = 0
    new_jobs = 0
    duplicates = 0

    start_time = time.time()

    with sync_playwright() as playwright:

        browser, page = launch_browser(playwright)

        search_jobs(page, search_title)

        for current_page in range(start_page, end_page + 1):

            retries = 3

            while retries > 0:

                try:

                    open_results_page(page, current_page)

                    jobs = extract_jobs(
                        page,
                        current_page,
                        search_title
                    )

                    log(f"Extracted {len(jobs)} jobs from page {current_page}")

                    page_new = 0
                    page_duplicates = 0

                    for job in jobs:

                        inserted = save_job(cursor, job)

                        total_jobs += 1

                        if inserted:

                            page_new += 1
                            new_jobs += 1

                        else:

                            page_duplicates += 1
                            duplicates += 1

                    conn.commit()

                    elapsed = time.time() - start_time

                    completed = current_page - start_page + 1
                    total_pages = end_page - start_page + 1

                    average = elapsed / completed

                    remaining = average * (total_pages - completed)

                    print("\n" + "=" * 60)

                    print(f"Page           : {current_page}/{end_page}")
                    print(f"Jobs Found     : {len(jobs)}")
                    print(f"New Jobs       : {page_new}")
                    print(f"Duplicates     : {page_duplicates}")
                    print(f"Total Scraped  : {total_jobs}")
                    print(f"Database Total : {new_jobs}")
                    print(f"Elapsed        : {format_time(elapsed)}")
                    print(f"Remaining ETA  : {format_time(remaining)}")

                    print("=" * 60)

                    save_resume(
                        search_title,
                        current_page + 1
                    )

                    break

                except TimeoutError:

                    retries -= 1

                    log(
                        f"Timeout on page {current_page}. "
                        f"Retries left: {retries}"
                    )

                    page.reload()

                except Exception as e:

                    retries -= 1

                    log(
                        f"Error on page {current_page}: {e}"
                    )

                    page.reload()

            else:

                log(f"Skipping page {current_page}")

        input("\nPress ENTER to close the browser...")
        browser.close()

    close_database(conn)

    delete_resume()

    print("\n")

    print("=" * 60)

    print("SCRAPING FINISHED")

    print("=" * 60)

    print(f"Search          : {search_title}")
    print(f"Pages           : {start_page} - {end_page}")
    print(f"Jobs Processed  : {total_jobs}")
    print(f"New Jobs Saved  : {new_jobs}")
    print(f"Duplicates      : {duplicates}")
    print(f"Elapsed Time    : {format_time(time.time()-start_time)}")

    print("=" * 60)

    # ==========================================================
# MAIN
# ==========================================================

def main():

    log("=" * 60)
    log("STEPSTONE JOB SCRAPER STARTED")
    log("=" * 60)

    settings = get_scrape_settings()

    if settings is None:

        log("User cancelled the scraper.")

        return

    try:

        scrape_jobs(settings)

    except KeyboardInterrupt:

        log("Scraper stopped by user.")

    except Exception as e:

        log(f"Fatal Error: {e}")

        raise


if __name__ == "__main__":

    main()