from playwright.sync_api import sync_playwright

PROFILE_PATH = r"C:\Users\yasho\Desktop\Job_Automation_Project\browser_profile"

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        channel="chrome",
        headless=False
    )

    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.stepstone.de")

    input("\nLog into Stepstone, then press ENTER...")

    context.close()