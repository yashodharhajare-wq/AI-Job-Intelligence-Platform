from playwright.sync_api import sync_playwright

CHROME_PROFILE = r"C:\Users\yasho\AppData\Local\Google\Chrome\User Data"

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=CHROME_PROFILE,
        channel="chrome",
        headless=False
    )

    page = context.new_page()

    page.goto("https://www.stepstone.de")

    input("Press ENTER to close...")

    context.close()