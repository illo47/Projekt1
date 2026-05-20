import requests
import json
import os
import pandas as pd
from calendar import monthrange
import calendar
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------
# 1) Session aus gespeicherter Login-Session laden
# ---------------------------------------------------------
def load_session_from_storage():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        # Cookies extrahieren
        cookies = context.cookies()

        sessid = None
        csrf = None

        for c in cookies:
            if c["name"] == "FS_SESSID":
                sessid = c["value"]
            if c["name"] == "FS_CSRF_TOKEN":
                csrf = c["value"]

        browser.close()

    if not sessid or not csrf:
        raise Exception("Fehler: FS_SESSID oder CSRF Token nicht gefunden.")

    session = requests.Session()
    session.cookies.set("FS_SESSID", sessid, domain="foodsharing.de")
    session.cookies.set("FS_CSRF_TOKEN", csrf, domain="foodsharing.de")

    session.headers.update({
        "Cookie": f"FS_SESSID={sessid}; FS_CSRF_TOKEN={csrf}",
        "X-CSRF-Token": csrf,
        "User-Agent": "Mozilla/5.0"
    })

    return session


# ---------------------------------------------------------
# 2) Excel-Datei finden
# ---------------------------------------------------------
def find_excel_file():
    for file in os.listdir():
        if file.endswith(".xlsx"):
            return file
    return None


# ---------------------------------------------------------
# 3) IDs aus Excel laden
# ---------------------------------------------------------
def load_ids_from_excel():
    excel_file = find_excel_file()

    if not excel_file:
        print("Keine Excel-Datei im Ordner gefunden.")
        return {}

    df = pd.read_excel(excel_file, sheet_name="Betriebe", usecols="C:D")
    df.columns = ["Kategorie", "ID"]
    df = df.dropna()

    category_dict = {}

    for _, row in df.iterrows():
        category = str(row["Kategorie"]).strip()
        store_id = str(int(row["ID"]))

        if category not in category_dict:
            category_dict[category] = []

        category_dict[category].append(store_id)

    return category_dict


# ---------------------------------------------------------
# 4) JSON für IDs herunterladen
# ---------------------------------------------------------
def download_json_for_ids(session, ids, output_dir, start_date, end_date, month_name, year):
    base_url = "https://foodsharing.de/api/stores/{}/pickups/history/{}/{}"

    os.makedirs(output_dir, exist_ok=True)

    for id in ids:
        url = base_url.format(id, start_date, end_date)

        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()

            output_file = os.path.join(output_dir, f"{id}_{month_name}_{year}.json")

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print(f"Daten für ID {id} gespeichert.")

        except requests.exceptions.RequestException as e:
            print(f"Fehler bei ID {id}: {e}")


# ---------------------------------------------------------
# 5) Hauptprogramm
# ---------------------------------------------------------
def main():
    # Monat/Jahr aus Umgebungsvariablen (Railway Cron)
    # YEAR/MONTH aus Environment oder Eingabe
    year_env = os.getenv("YEAR")
    month_env = os.getenv("MONTH")

    if year_env and month_env:
        year = int(year_env)
        month = int(month_env)
    else:
        print("Keine Environment-Variablen gefunden. Bitte lokal eingeben:")
        year = int(input("Jahr (z. B. 2026): "))
        month = int(input("Monat (1–12): "))


    month_str = f"{month:02d}"
    days_in_month = monthrange(year, month)[1]

    start_date = f"{year}-{month_str}-01T00:00:00.000Z"
    end_date = f"{year}-{month_str}-{days_in_month}T23:59:59.000Z"
    month_name = calendar.month_name[month]

    session = load_session_from_storage()
    category_ids = load_ids_from_excel()

    base_output_dir = os.path.join("output", f"{year}_{month_str}")

    for category, ids in category_ids.items():
        output_dir = os.path.join(base_output_dir, category)
        download_json_for_ids(session, ids, output_dir, start_date, end_date, month_name, year)


if __name__ == "__main__":
    main()
