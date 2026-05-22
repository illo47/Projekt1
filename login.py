from playwright.sync_api import sync_playwright
import os
import time

def main():
    email = os.environ["FS_EMAIL"]
    password = os.environ["FS_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )

        context = browser.new_context()
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        print("Öffne Login-Seite…")
        page.goto("https://foodsharing.de/?page=login", wait_until="domcontentloaded")

        # Cookie-Banner
        try:
            page.click("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
        except:
            pass

        # Warten auf E-Mail-Feld
        try:
            page.wait_for_selector("input[type='email']", timeout=15000)
        except:
            page.screenshot(path="login_error.png")
            raise Exception("Login-Feld nicht sichtbar. Screenshot gespeichert.")

        # E-Mail eingeben
        page.fill("input[type='email']", email)

        # Passwort eingeben
        page.fill("input[type='password']", password)

        # Login klicken
        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")
        time.sleep(2)

        if "login" in page.url:
            page.screenshot(path="login_failed.png")
            raise Exception("Login fehlgeschlagen! Screenshot gespeichert.")

        context.storage_state(path="auth.json")
        print("auth.json erfolgreich erzeugt.")

        browser.close()

if __name__ == "__main__":
    main()
