
import csv
import json

import requests

# Параметри програми (винесені у змінні для повторного використання)
BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
COUNTRIES = "UA;US"                 # коди країн: Україна та США
INDICATOR = "SP.DYN.LE00.IN"        # Life expectancy at birth, total (years)
DATE_RANGE = "2010:2019"            # діапазон років
PER_PAGE = 500                      # кількість записів на сторінці
TIMEOUT = 10                        # таймаут запиту, секунди

JSON_FILE = "life_expectancy.json"
CSV_FILE = "life_expectancy.csv"
CSV_DELIMITER = ";"                 # як у прикладі з методички
CSV_HEADER = ["Country Name", "Country Code", "Year",
              "Life expectancy at birth, total (years)"]


# 1. Одержання даних через API

def build_url(countries, indicator):
    """Формує URL-адресу API відповідно до варіанта."""
    return BASE_URL.format(countries=countries, indicator=indicator)


def fetch_data(countries, indicator, date_range, per_page):
    """Надсилає HTTP-запит до API Світового банку і повертає JSON-дані."""
    url = build_url(countries, indicator)
    params = {"date": date_range, "format": "json", "per_page": per_page}

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as error:
        # помилки виконання HTTP-запиту (немає мережі, таймаут тощо)
        print(f"Помилка виконання HTTP-запиту: {error}")
        return None

    # перевірка успішності запиту за кодом відповіді
    if response.status_code != 200:
        print(f"Помилка отримання даних. Код відповіді: {response.status_code}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Помилка: відповідь сервера не є коректним JSON.")
        return None

    print("Дані успішно отримано")
    return data


# 2. Перевірка коректності даних
def validate_data(data):
    """Перевіряє структуру отриманих даних перед збереженням."""
    # очікуємо [метадані, список_записів]
    if not isinstance(data, list) or len(data) < 2:
        print("Помилка: некоректна структура відповіді API.")
        return False

    records = data[1]
    if not records:  # None або порожній список
        print("Помилка: відсутні одержані дані.")
        return False

    required_keys = ("country", "countryiso3code", "date", "value")
    for item in records:
        if not all(key in item for key in required_keys):
            print("Помилка: у записі відсутні необхідні поля.")
            return False
    return True


# 3. Збереження даних у JSON
def save_json(data, filename):
    """Зберігає дані у JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"Створено файл {filename}")
    return True

# 4. Перетворення у CSV та збереження
def convert_to_csv_rows(data):
    """Виділяє з JSON потрібні поля; записи без значення пропускаються."""
    rows = []
    for item in data[1]:
        if item["value"] is not None:
            rows.append([
                item["country"]["value"],
                item["countryiso3code"],
                item["date"],
                round(item["value"], 3),
            ])
    # сортування: країна, потім рік
    rows.sort(key=lambda row: (row[0], row[2]))
    return rows


def save_csv(rows, filename):
    """Зберігає рядки у CSV-файл."""
    if not rows:
        print("Помилка: немає даних для запису у CSV.")
        return False
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=CSV_DELIMITER)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows)
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"Створено файл {filename}")
    return True


# 5. Виведення результатів
def print_file(filename, title):
    """Читає файл і виводить його вміст на екран."""
    print(f"\n{title}")
    print("-" * 50)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            print(file.read())
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено.")
    except OSError as error:
        print(f"Помилка читання файлу {filename}: {error}")


# Головна функція
def main():
    data = fetch_data(COUNTRIES, INDICATOR, DATE_RANGE, PER_PAGE)
    if data is None or not validate_data(data):
        return

    if not save_json(data, JSON_FILE):
        return

    rows = convert_to_csv_rows(data)
    if not save_csv(rows, CSV_FILE):
        return

    print_file(JSON_FILE, "Зміст JSON:")
    print_file(CSV_FILE, "Зміст CSV:")


if __name__ == "__main__":
    main()