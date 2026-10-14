
import csv

import matplotlib.pyplot as plt
import numpy as np

# Параметри програми
INPUT_FILE = "life_expectancy.csv"
DELIMITER = ";"

COUNTRY1 = "Ukraine"
COUNTRY2 = "United States"
INDICATOR = "Life expectancy at birth, total (years)"

COL_COUNTRY = "Country Name"
COL_YEAR = "Year"
COL_VALUE = "Life expectancy at birth, total (years)"

LINE_FILE = "line_chart.png"
BAR_FILE = "bar_chart.png"
PIE_FILE = "pie_chart.png"

# 1. Завантаження та обробка даних
def load_data(filename):
    """
    Читає CSV і повертає словник {країна: {рік: значення}}.
    Повертає None, якщо файл не вдалося відкрити або прочитати.
    """
    data = {}
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
                data.setdefault(row[COL_COUNTRY], {})[year] = value
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено! Скопіюйте його з практичної роботи 5.")
        return None
    except (OSError, csv.Error) as error:
        print(f"Помилка відкриття або читання файлу {filename}: {error}")
        return None

    if not data:
        print(f"У файлі {filename} немає даних для побудови графіків.")
        return None
    return data


def build_arrays(data, country1, country2):
    """Формує масиви: роки та значення показника для двох країн."""
    for country in (country1, country2):
        if country not in data:
            print(f"Помилка: країни {country} немає в завантажених даних.")
            return None

    years = sorted(set(data[country1]) & set(data[country2]))
    if not years:
        print("Помилка: немає спільних років для двох країн.")
        return None

    values1 = np.array([data[country1][year] for year in years])
    values2 = np.array([data[country2][year] for year in years])
    return np.array(years), values1, values2

# 2. Введення та перевірка даних користувача
def ask_country(data):
    """Запитує назву країни і перевіряє її наявність у завантажених даних."""
    lookup = {name.lower(): name for name in data}
    print("\nДоступні країни:", ", ".join(sorted(data)))
    while True:
        text = input("Введіть назву країни для стовпчастої діаграми: ").strip()
        if text.lower() in lookup:
            return lookup[text.lower()]
        print(f"Помилка: країни \"{text}\" немає в завантажених даних.")


def ask_year(years):
    """Запитує рік, який присутній у даних."""
    first, last = int(years[0]), int(years[-1])
    while True:
        text = input(f"Введіть рік для кругової діаграми ({first}-{last}): ").strip()
        if text.isdigit() and int(text) in years:
            return int(text)
        print(f"Помилка: введіть рік від {first} до {last}.")


# 3. Побудова графіків
def save_figure(filename):
    """Зберігає поточний графік у PNG-файл (для звіту)."""
    try:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Графік збережено у файл {filename}")
    except OSError as error:
        print(f"Помилка збереження файлу {filename}: {error}")


def plot_line(years, values1, values2, country1, country2):
    """Лінійний графік динаміки показника для двох країн."""
    plt.figure(figsize=(8, 5))
    plt.plot(years, values1, marker="o", label=country1)
    plt.plot(years, values2, marker="o", label=country2)
    plt.title(f"Indicator dynamics for {country1} and {country2}", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel(INDICATOR, fontsize=12)
    plt.xticks(years)
    plt.legend()
    plt.grid(True)
    save_figure(LINE_FILE)
    plt.show()


def plot_bar(years, values, country):
    """Стовпчаста діаграма значень показника за роками для однієї країни."""
    plt.figure(figsize=(8, 5))
    bars = plt.bar(years, values, color="tab:blue")
    plt.bar_label(bars, fmt="%.1f", fontsize=8)
    plt.title(f"{INDICATOR}: {country}", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel(INDICATOR, fontsize=12)
    plt.xticks(years)
    plt.grid(True, axis="y")
    save_figure(BAR_FILE)
    plt.show()


def pie_label(pct, allvals):
    """Підпис сектора: відсоток і абсолютне значення."""
    absolute = np.round(pct / 100 * np.sum(allvals), 2)
    return f"{pct:.1f}%\n({absolute})"


def plot_pie(year, value1, value2, country1, country2):
    """Кругова діаграма порівняння двох країн за обраний рік."""
    values = np.array([value1, value2])
    labels = [country1, country2]

    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        values,
        labels=labels,
        autopct=lambda pct: pie_label(pct, values),
    )
    plt.setp(autotexts, size=10, weight="bold")
    plt.title(f"Indicator comparison for {country1} and {country2} ({year})",
              fontsize=14)
    save_figure(PIE_FILE)
    plt.show()

# Головна функція
def main():
    data = load_data(INPUT_FILE)
    if data is None:
        return

    arrays = build_arrays(data, COUNTRY1, COUNTRY2)
    if arrays is None:
        return
    years, values1, values2 = arrays

    # 1. Лінійний графік
    plot_line(years, values1, values2, COUNTRY1, COUNTRY2)

    # 2. Стовпчаста діаграма для країни, яку вводить користувач
    country = ask_country(data)
    country_years = np.array(sorted(data[country]))
    country_values = np.array([data[country][year] for year in country_years])
    plot_bar(country_years, country_values, country)

    # 3. Кругова діаграма за рік, який вводить користувач
    year = ask_year(years)
    index = int(np.where(years == year)[0][0])
    plot_pie(year, values1[index], values2[index], COUNTRY1, COUNTRY2)


if __name__ == "__main__":
    main()