import pandas as pd
import requests

# Параметри програми
INPUT_FILE = "life_expectancy.csv"  # файл з практичної роботи 5
OUTPUT_FILE = "life_expectancy_extended.csv"  # доповнений файл
DELIMITER = ";"

BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
COUNTRIES = "UA;US"
DATE_RANGE = "2010:2019"
PER_PAGE = 500
TIMEOUT = 10

NEW_INDICATORS = {
    "SP.POP.TOTL": "Population, total",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
}

KEY_COLUMNS = ["Country Code", "Year"]


# Завантаження вихідного CSV
def load_base(filename):
    """Завантажує CSV з практичної роботи 5 у DataFrame."""
    try:
        df = pd.read_csv(filename, sep=DELIMITER, encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"Помилка: файл {filename} не знайдено! "
              "Скопіюйте його з практичної роботи 5.")
        return None
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        print(f"Помилка читання файлу {filename}: {error}")
        return None

    if df.empty or not set(KEY_COLUMNS).issubset(df.columns):
        print(f"Помилка: у файлі {filename} немає потрібних даних або стовпців.")
        return None
    print(f"Файл {filename} успішно завантажено ({len(df)} рядків)")
    return df


# Отримання нових показників через API
def fetch_indicator(indicator, column_name):
    """Отримує показник через API; повертає DataFrame: код країни, рік, значення."""
    url = BASE_URL.format(countries=COUNTRIES, indicator=indicator)
    params = {"date": DATE_RANGE, "format": "json", "per_page": PER_PAGE}

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as error:
        print(f"Помилка виконання HTTP-запиту ({indicator}): {error}")
        return None

    if response.status_code != 200:
        print(f"Помилка отримання даних ({indicator}). "
              f"Код відповіді: {response.status_code}")
        return None

    try:
        data = response.json()
    except ValueError:
        print(f"Помилка: відповідь для {indicator} не є коректним JSON.")
        return None

    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        print(f"Помилка: відсутні дані для показника {indicator}.")
        return None

    rows = []
    for item in data[1]:
        if item.get("value") is None:
            continue
        rows.append({
            "Country Code": item["countryiso3code"],
            "Year": int(item["date"]),
            column_name: item["value"],
        })

    if not rows:
        print(f"Помилка: для показника {indicator} немає значень.")
        return None

    print(f"Отримано показник {column_name}: {len(rows)} записів")
    return pd.DataFrame(rows)


# Об'єднання та збереження
def extend_dataset(df):
    """Додає до DataFrame нові показники (об'єднання за країною та роком)."""
    for indicator, column_name in NEW_INDICATORS.items():
        new_data = fetch_indicator(indicator, column_name)
        if new_data is None:
            return None
        df = df.merge(new_data, on=KEY_COLUMNS, how="left")
    return df


def save_dataset(df, filename):
    """Зберігає доповнений DataFrame у CSV."""
    try:
        df.to_csv(filename, sep=DELIMITER, index=False, encoding="utf-8-sig")
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"Створено файл {filename}")
    return True


def main():
    df = load_base(INPUT_FILE)
    if df is None:
        return

    extended = extend_dataset(df)
    if extended is None:
        return

    if save_dataset(extended, OUTPUT_FILE):
        pd.set_option("display.width", 200)
        pd.set_option("display.max_columns", None)
        print("\nДоповнений набір даних:")
        print(extended)


if __name__ == "__main__":
    main()