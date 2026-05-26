from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://foodsharing.de/?page=login")

        input("Bitte manuell einloggen und ENTER drücken...")

        context.storage_state(path="auth.json")
        print("auth.json gespeichert!")

if __name__ == "__main__":
    main()
