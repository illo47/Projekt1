import requests
import json
import os
import pandas as pd
from calendar import monthrange
import calendar
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------
# Immer den letzten Monat verwenden
# ---------------------------------------------------------

from datetime import datetime, timedelta

def get_previous_month():
    today = datetime.today()
    first_of_this_month = today.replace(day=1)
    last_month_last_day = first_of_this_month - timedelta(days=1)
    year = last_month_last_day.year
    month = last_month_last_day.month
    return year, month


# ---------------------------------------------------------
# 1) Session aus gespeicherter Login-Session laden
# ---------------------------------------------------------
import requests
import os

def login_via_api():
    email = os.environ["FS_EMAIL"]
    password = os.environ["FS_PASSWORD"]

    url = "https://foodsharing.de/api/user/login"

    payload = {
        "email": steffen.zindel@gmail.com,
        "password": 7s@dRR&$PwY!yg
    }

    session = requests.Session()
    response = session.post(url, json=payload)

    if response.status_code != 200:
        raise Exception("Login fehlgeschlagen: " + response.text)

    # Cookies extrahieren
    sessid = session.cookies.get("FS_SESSID")
    csrf = session.cookies.get("FS_CSRF_TOKEN")

    if not sessid or not csrf:
        raise Exception("Login erfolgreich, aber Cookies fehlen.")

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
    start_ts = f"{start_date}T00:00:00.000Z"
    end_ts = f"{end_date}T23:59:59.000Z"
    
    base_url = "https://foodsharing.de/api/stores/{}/pickups/history/{}/{}"

    os.makedirs(output_dir, exist_ok=True)

    for id in ids:
        url = base_url.format(id, start_ts, end_ts)

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
    year, month = get_previous_month()
    # Start- und Enddatum des Vormonats berechnen
    start_date = f"{year}-{month:02d}-01"

    # letzter Tag des Monats:
    if month == 12:
        end_date = f"{year}-12-31"
    else:
        next_month = datetime(year, month, 1).replace(day=28) + timedelta(days=4)
        last_day = (next_month - timedelta(days=next_month.day)).day
        end_date = f"{year}-{month:02d}-{last_day:02d}"

    # Für Dateinamen
    month_name = f"{month:02d}"

    month_str = f"{month:02d}"
    year_str = str(year)

    print(f"Starte Verarbeitung für {year_str}-{month_str}")

    session = login_via_api()
    category_ids = load_ids_from_excel()

    base_output_dir = os.path.join("output", f"{year}_{month_str}")

    for category, ids in category_ids.items():
        output_dir = os.path.join(base_output_dir, category)
        download_json_for_ids(session, ids, output_dir, start_date, end_date, month_name, year)


if __name__ == "__main__":
    main()
