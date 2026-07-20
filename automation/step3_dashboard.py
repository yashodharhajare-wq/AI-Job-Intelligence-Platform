import sqlite3
import webbrowser
import customtkinter as ctk

DB = "jobs.db"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Job Dashboard")
        self.geometry("1200x700")

        self.current_job = None

        # ---------------- Left Panel ----------------

        left = ctk.CTkFrame(self)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.search = ctk.CTkEntry(left, placeholder_text="Search...")
        self.search.pack(fill="x", padx=10, pady=10)
        self.search.bind("<KeyRelease>", lambda e: self.load_jobs())

        self.status = ctk.CTkOptionMenu(
            left,
            values=[
                "NEW",
                "EXCLUDED",
                "APPLIED",
                "REJECTED",
                "INTERVIEW",
                "OFFER",
                "ALL"
            ],
            command=lambda x: self.load_jobs()
        )

        self.status.set("NEW")
        self.status.pack(fill="x", padx=10)

        self.job_list = ctk.CTkTextbox(left, width=500)
        self.job_list.pack(fill="both", expand=True, padx=10, pady=10)

        self.job_list.bind("<ButtonRelease-1>", self.job_clicked)

        # ---------------- Right Panel ----------------

        right = ctk.CTkFrame(self)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            right,
            text="Select a Job",
            font=("Arial", 22, "bold")
        )
        self.title_label.pack(anchor="w", padx=20, pady=10)

        self.company_label = ctk.CTkLabel(right, text="")
        self.company_label.pack(anchor="w", padx=20)

        self.location_label = ctk.CTkLabel(right, text="")
        self.location_label.pack(anchor="w", padx=20)

        self.reason_label = ctk.CTkLabel(right, text="")
        self.reason_label.pack(anchor="w", padx=20, pady=10)
        self.history_label = ctk.CTkTextbox(
            right,
            height=140
        )
        self.history_label.pack(fill="x", padx=20, pady=(0,10))

        ctk.CTkLabel(right, text="Notes").pack(anchor="w", padx=20)

        self.notes = ctk.CTkTextbox(right, height=180)
        self.notes.pack(fill="x", padx=20)

        button_frame = ctk.CTkFrame(right)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Open Job",
            command=self.open_job
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Applied",
            command=lambda: self.change_status("APPLIED")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Rejected",
            command=lambda: self.change_status("REJECTED")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="New",
            command=lambda: self.change_status("NEW")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Save Notes",
            command=self.save_notes
        ).pack(side="right")

        self.load_jobs()

    # ------------------------------------------------

    def db(self):
        return sqlite3.connect(DB)

    # ------------------------------------------------

    def load_jobs(self):

        search = self.search.get().lower()

        status = self.status.get()

        conn = self.db()
        cur = conn.cursor()

        if status == "ALL":

            cur.execute("""
                SELECT id,title,company
                FROM jobs
                ORDER BY scraped_at DESC
            """)

        else:

            cur.execute("""
                SELECT id,title,company
                FROM jobs
                WHERE status=?
                ORDER BY scraped_at DESC
            """, (status,))

        rows = cur.fetchall()

        conn.close()

        self.jobs = {}

        self.job_list.delete("1.0", "end")

        for job_id, title, company in rows:

            display = f"{title} | {company}"

            if search:
                text = display.lower()

                if search not in text:
                    continue

            self.jobs[display] = job_id

            self.job_list.insert("end", display + "\n")

    # ------------------------------------------------

    def job_clicked(self, event):

        try:

            index = self.job_list.index("insert linestart")

            line = self.job_list.get(index, index + " lineend").strip()

            if line not in self.jobs:
                return

            job_id = self.jobs[line]

            conn = self.db()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    title,
                    company,
                    location,
                    link,
                    status,
                    reason,
                    notes
                FROM jobs
                WHERE id=?
            """, (job_id,))

            self.current_job = cur.fetchone()

            (
                _,
                title,
                company,
                location,
                link,
                status,
                reason,
                notes
            ) = self.current_job

            self.title_label.configure(text=title)

            self.company_label.configure(text=f"Company : {company}")

            self.location_label.configure(text=f"Location : {location}")

            self.reason_label.configure(text=f"Reason : {reason}")

            # ----------------------------------------
# Job History (Possible Repost)
# ----------------------------------------

            cur.execute("""
            SELECT
                scraped_at,
                status
            FROM jobs
            WHERE
                LOWER(TRIM(company)) = LOWER(TRIM(?))
            AND LOWER(TRIM(title)) = LOWER(TRIM(?))
            ORDER BY scraped_at
            """, (company, title))

            history = cur.fetchall()

            self.history_label.delete("1.0", "end")

            if len(history) == 1:

                self.history_label.insert(
                    "end",
                    "First time seen."
                )

            else:

                self.history_label.insert(
                    "end",
                    "⚠ POSSIBLE REPOST\n\n"
                )

                self.history_label.insert(
                    "end",
                    f"Occurrences : {len(history)}\n\n"
                )

                for date, old_status in history:

                    self.history_label.insert(
                        "end",
                        f"{date[:10]}    {old_status}\n"
                    )
            conn.close()

            self.notes.delete("1.0", "end")

            if notes:
                self.notes.insert("1.0", notes)

        except:
            pass

    # ------------------------------------------------

    def open_job(self):

        if not self.current_job:
            return

        webbrowser.open(self.current_job[4])

    # ------------------------------------------------

    def change_status(self, status):

        if not self.current_job:
            return

        conn = self.db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE jobs
            SET status=?
            WHERE id=?
        """, (status, self.current_job[0]))

        conn.commit()

        conn.close()

        self.load_jobs()

    # ------------------------------------------------

    def save_notes(self):

        if not self.current_job:
            return

        notes = self.notes.get("1.0", "end").strip()

        conn = self.db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE jobs
            SET notes=?
            WHERE id=?
        """, (notes, self.current_job[0]))

        conn.commit()

        conn.close()


Dashboard().mainloop()