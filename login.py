from playwright.sync_api import sync_playwright
import os

def main():
    email = os.environ["FS_EMAIL"]
    password = os.environ["FS_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://foodsharing.de/?page=login")

        # Neue, funktionierende Selektoren
        page.fill("#login-email", email)
        page.fill("#login-password", password)

        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")

        context.storage_state(path="auth.json")
        browser.close()

if __name__ == "__main__":
    main()
