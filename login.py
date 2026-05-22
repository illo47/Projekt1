from playwright.sync_api import sync_playwright
import os
import time

def main():
    email = os.environ["FS_EMAIL"]
    password = os.environ["FS_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Öffne Login-Seite…")
        page.goto("https://foodsharing.de/?page=login", wait_until="domcontentloaded")

        # 1. Cookie-Banner abfangen
        try:
            page.wait_for_selector("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
            page.click("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            print("Cookie-Banner akzeptiert.")
        except:
            print("Kein Cookie-Banner gefunden.")

        # 2. Sicherstellen, dass wir auf der Login-Seite sind
        if "login" not in page.url:
            print("Nicht auf Login-Seite – versuche Redirect…")
            page.goto("https://foodsharing.de/?page=login", wait_until="networkidle")

        # 3. Warten auf ein Eingabefeld (egal welches)
        try:
            page.wait_for_selector("input[type='email'], #login-email, input[name='email']", timeout=10000)
        except:
            page.screenshot(path="login_error.png")
            raise Exception("Login-Felder nicht gefunden! Screenshot gespeichert: login_error.png")

        # 4. Mehrere mögliche Selektoren testen
        selectors_email = ["#login-email", "input[type='email']", "input[name='email']"]
        selectors_password = ["#login-password", "input[type='password']", "input[name='password']"]

        filled = False
        for sel in selectors_email:
            try:
                page.fill(sel, email)
                filled = True
                print(f"E-Mail-Feld gefunden: {sel}")
                break
            except:
                pass

        if not filled:
            page.screenshot(path="login_error.png")
            raise Exception("Kein E-Mail-Feld gefunden! Screenshot gespeichert: login_error.png")

        filled = False
        for sel in selectors_password:
            try:
                page.fill(sel, password)
                filled = True
                print(f"Passwort-Feld gefunden: {sel}")
                break
            except:
                pass

        if not filled:
            page.screenshot(path="login_error.png")
            raise Exception("Kein Passwort-Feld gefunden! Screenshot gespeichert: login_error.png")

        # 5. Login-Button klicken
        try:
            page.click("button[type='submit']")
        except:
            page.screenshot(path="login_error.png")
            raise Exception("Login-Button nicht gefunden! Screenshot gespeichert: login_error.png")

        # 6. Warten bis eingeloggt
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 7. Prüfen ob Login erfolgreich war
        if "login" in page.url:
            page.screenshot(path="login_failed.png")
            raise Exception("Login fehlgeschlagen! Screenshot gespeichert: login_failed.png")

        # 8. Session speichern
        context.storage_state(path="auth.json")
        print("auth.json erfolgreich erzeugt.")

        browser.close()

if __name__ == "__main__":
    main()
