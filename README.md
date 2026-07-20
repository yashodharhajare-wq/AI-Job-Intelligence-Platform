# Career Intelligence Platform

> **A desktop application born out of fustration and need.**
>
> Instead of spending hours searching, filtering, tracking, and revisiting the same jobs, I wanted software that would do the repetitive work for me so I could focus on what actually matters—preparing good applications and interviews.

---

# The Problem

When I started applying for jobs after graduating in Germany, I expected the difficult part to be interviews.

Instead, I found myself spending hours every day simply searching.

The actual application often took less time than finding a suitable vacancy.

That was frustrating because searching wasn't creating value—it was just consuming time.

Every day looked almost identical.

- Open StepStone/ job platforms.
- Search using the same keywords.
- Apply filters again.
- platform shows 80% unrelated jobs (with keywords like praktikum, Monteur, buchhalter etc)
- if use different and strict keywords, fear of loosing genuine job.
- then scroll through hundreds of listings from multiple pages.
- filter unrelated jobs
- Wonder whether I had already seen a particular job.
- Check my Excel sheet to see if I had already applied.
- Open multiple browser tabs.
- Repeat the next day.

It wasn't difficult work.

It was repetitive and mentally exhausting work.

As the number of applications grew, so did the time spent simply organizing them.

I wanted to spend my time improving my resume, preparing for interviews, and writing better applications—not filtering jobs, scrolling 50 pages, remembering whether I'd already looked at a particular vacancy.

As an engineer, my first instinct wasn't to accept the repetitive process.

If a task is repeated every day, follows the same pattern, and doesn't require creativity, it's usually a good candidate for automation.

So instead of changing my routine, I built software to change it for me.

# The Solution
This application became my personal job-search assistant.

It remembers what I've already seen, tracks every application, filters opportunities that match my interests, and lets me focus on making better applications instead of managing them.

This project automatically opens chrome, logs into my account, collects jobs, stores them locally, filter them with exact keywords, keeps track of application status, and remembers my interaction with every job opportunity.

Instead of asking:

> "Have I seen this job before?"

the application already knows.

Instead of maintaining spreadsheets, everything is stored in a searchable database.

Instead of manually comparing jobs every day, I only review what's actually new.

The goal isn't to replace job searching.

The goal is to remove the repetitive work surrounding it.

---

# Features

- Automated job collection
- SQLite database
- Desktop dashboard
- Application tracking
- Search & filtering
- Personal notes
- Excel import
- Job history
- Possible repost detection
- Duplicate prevention

---

# Why This Project Matters

This project wasn't created to demonstrate Playwright or SQLite.

Those are simply tools.

The real objective was solving a workflow problem that I encountered every day.

The biggest lesson from building this project wasn't web scraping.

It was realizing that many hours are lost to repetitive tasks that computers are much better at handling.

---
Results

- Reduced daily job-search time from roughly 3 hours to 20 minutes.
- Eliminated the need for manual Excel tracking.
- Prevented reviewing the same postings repeatedly.
- Centralized the entire application process in one place.
- most Important - PEACE
---

# Looking Ahead

Although this application currently focuses on job searching, its architecture is intentionally generic.

The same workflow can be adapted for:

- Competitor monitoring
- Market intelligence
- Product tracking
- News aggregation
- Research automation
- Procurement monitoring
- Lead generation

The scraper, database, and dashboard remain the same.

Only the data source changes.

The next step is integrating AI so the software doesn't just collect information—it understands it.

Future AI capabilities include:

- Resume-job matching
- AI relevance scoring
- Company insights
- Skill gap analysis
- Job summarization
- Intelligent recommendations

The long-term vision is to evolve this from a job tracker into a reusable AI-powered information intelligence platform.
