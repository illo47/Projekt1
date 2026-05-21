from playwright.sync_api import sync_playwright
import json

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://foodsharing.de/?page=login")

        page.fill("input[name='email']", "${{ secrets.FS_EMAIL }}")
        page.fill("input[name='password']", "${{ secrets.FS_PASSWORD }}")
        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")

        context.storage_state(path="auth.json")
        browser.close()

if __name__ == "__main__":
    main()
