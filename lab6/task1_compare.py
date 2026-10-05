
import csv

# Параметри програми

INPUT_FILE = "life_expectancy.csv"      # файл з практичної роботи 5
OUTPUT_FILE = "comparison.csv"          # назва вихідного файлу за замовчуванням
DELIMITER = ";"

COUNTRY_UA = "Ukraine"
COUNTRY_US = "United States"
MIN_YEAR = 2010
MAX_YEAR = 2019

COL_COUNTRY = "Country Name"
COL_YEAR = "Year"
COL_VALUE = "Life expectancy at birth, total (years)"

OUTPUT_HEADER = ["Рік", "Україна", "США", "Різниця (США - Україна)", "Вищий показник"]
FORBIDDEN_CHARS = '<>:"/\\|?*'



# Введення та перевірка даних користувача
def ask_year(prompt, min_year, max_year):
    """Запитує рік, поки користувач не введе коректне ціле число у діапазоні."""
    while True:
        text = input(prompt).strip()
        if not text.isdigit():
            print("Помилка: потрібно ввести ціле число, наприклад 2015.")
            continue
        year = int(text)
        if not min_year <= year <= max_year:
            print(f"Помилка: рік має бути від {min_year} до {max_year}.")
            continue
        return year


def ask_filename(prompt, default):
    """Запитує назву файлу; Enter - значення за замовчуванням. Додає .csv."""
    while True:
        name = input(prompt).strip()
        if not name:
            return default
        if any(char in name for char in FORBIDDEN_CHARS):
            print(f"Помилка: назва не повинна містити символи {FORBIDDEN_CHARS}")
            continue
        if not name.lower().endswith(".csv"):
            name += ".csv"
        return name


# Читання даних з CSV
def read_csv_data(filename):
    """
    Читає CSV-файл і повертає словник {(країна, рік): значення}.
    Повертає None, якщо файл не вдалося відкрити або він некоректний.
    """
    values = {}
    try:
        with open(filename, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=DELIMITER)
            needed = {COL_COUNTRY, COL_YEAR, COL_VALUE}
            if reader.fieldnames is None or not needed.issubset(reader.fieldnames):
                print(f"Помилка: у файлі {filename} немає потрібних стовпців.")
                return None
            for row in reader:
                try:
                    year = int(row[COL_YEAR])
                    value = float(row[COL_VALUE].replace(",", "."))
                except (ValueError, AttributeError):
                    continue  # пропускаємо рядки з некоректними даними
                values[(row[COL_COUNTRY], year)] = value
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено! Спершу виконайте практичну роботу 5.")
        return None
    except OSError as error:
        print(f"Помилка відкриття файлу {filename}: {error}")
        return None

    if not values:
        print(f"У файлі {filename} немає даних для обробки.")
        return None
    return values


# Порівняння показників
def compare_countries(values, start_year, end_year):
    """Порівнює значення США та України по роках; повертає список рядків."""
    rows = []
    for year in range(start_year, end_year + 1):
        ua = values.get((COUNTRY_UA, year))
        us = values.get((COUNTRY_US, year))

        if ua is None or us is None:
            rows.append([year,
                         "" if ua is None else f"{ua:.2f}",
                         "" if us is None else f"{us:.2f}",
                         "", "немає даних"])
            continue

        difference = round(us - ua, 2)
        if difference > 0:
            higher = "США"
        elif difference < 0:
            higher = "Україна"
        else:
            higher = "однакові"
        rows.append([year, f"{ua:.2f}", f"{us:.2f}", f"{difference:.2f}", higher])
    return rows


# Збереження та виведення результатів
def save_comparison(rows, filename):
    """Зберігає результати порівняння у новий CSV-файл із заголовками."""
    try:
        with open(filename, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=DELIMITER)
            writer.writerow(OUTPUT_HEADER)
            writer.writerows(rows)
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"\nРезультати збережено у файл {filename}")
    return True


def print_comparison(rows):
    """Виводить таблицю порівняння на екран."""
    print("\nПорівняння очікуваної тривалості життя (років):")
    print("-" * 70)
    print(f"{OUTPUT_HEADER[0]:<6}{OUTPUT_HEADER[1]:<12}{OUTPUT_HEADER[2]:<10}"
          f"{OUTPUT_HEADER[3]:<26}{OUTPUT_HEADER[4]}")
    print("-" * 70)
    for year, ua, us, diff, higher in rows:
        print(f"{year:<6}{ua:<12}{us:<10}{diff:<26}{higher}")


# Головна функція
def main():
    values = read_csv_data(INPUT_FILE)
    if values is None:
        return

    print(f"Порівняння показників: {COUNTRY_US} та {COUNTRY_UA}")
    start_year = ask_year(f"Введіть початковий рік ({MIN_YEAR}-{MAX_YEAR}): ",
                          MIN_YEAR, MAX_YEAR)
    end_year = ask_year(f"Введіть кінцевий рік ({start_year}-{MAX_YEAR}): ",
                        start_year, MAX_YEAR)
    output_name = ask_filename(
        f"Введіть назву вихідного файлу (Enter - {OUTPUT_FILE}): ", OUTPUT_FILE)

    rows = compare_countries(values, start_year, end_year)
    print_comparison(rows)
    save_comparison(rows, output_name)


if __name__ == "__main__":
    main()