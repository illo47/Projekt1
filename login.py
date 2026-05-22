from playwright.sync_api import sync_playwright
import os
import time

def safe_screenshot(page, name):
    try:
        page.screenshot(path=name)
        print(f"Screenshot gespeichert: {name}")
    except:
        print("Screenshot konnte nicht gespeichert werden.")

def main():
    email = os.environ["FS_EMAIL"]
    password = os.environ["FS_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Öffne Login-Seite…")
        page.goto("https://foodsharing.de/?page=login", wait_until="domcontentloaded")

        # Cookie-Banner
        try:
            page.click("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=3000)
        except:
            pass

        # Warten auf E-Mail-Feld
        try:
            page.wait_for_selector("input[type='email']", timeout=8000)
        except:
            safe_screenshot(page, "login_error.png")
            raise Exception("Login-Feld nicht sichtbar.")

        # E-Mail eingeben
        try:
            page.fill("input[type='email']", email)
        except:
            safe_screenshot(page, "login_error.png")
            raise

        # Passwort eingeben
        try:
            page.fill("input[type='password']", password)
        except:
            safe_screenshot(page, "login_error.png")
            raise

        # Login klicken
        try:
            page.click("button[type='submit']")
        except:
            safe_screenshot(page, "login_error.png")
            raise

        page.wait_for_load_state("networkidle")
        time.sleep(2)

        if "login" in page.url:
            safe_screenshot(page, "login_failed.png")
            raise Exception("Login fehlgeschlagen.")

        context.storage_state(path="auth.json")
        print("auth.json erfolgreich erzeugt.")

        browser.close()

if __name__ == "__main__":
    main()
