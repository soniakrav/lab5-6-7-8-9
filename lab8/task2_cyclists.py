import warnings

import matplotlib.pyplot as plt
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

# Параметри програми
DATA_FILE = "comptagevelo20152.csv" # CSV-файл за 2015 рік
YEAR = 2015  # рік за варіантом 13
ENCODINGS = ("utf-8-sig", "latin1")  # кодування, які пробуємо по черзі
TOP_TRACKS = 3  # кількість велодоріжок для аналізу місяців
PLOT_FILE = "track_dynamics.png"

MONTHS = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
          "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
MONTHS_SHORT = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
                "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"]


def print_title(text):
    """Виводить заголовок розділу."""
    print(f"\n{text}")
    print("-" * 60)


# 1. Завантаження та підготовка даних
def read_file(filename):
    """Читає CSV (роздільник визначається автоматично, кодування підбирається)."""
    for encoding in ENCODINGS:
        try:
            return pd.read_csv(filename, sep=None, engine="python",
                               encoding=encoding)
        except UnicodeDecodeError:
            continue
    print("Помилка: не вдалося визначити кодування файлу.")
    return None


def find_date_column(df):
    """Шукає стовпець з датою: за назвою Date/Дата, інакше - перший стовпець."""
    for column in df.columns:
        if str(column).strip().lower() in ("date", "дата"):
            return column
    return df.columns[0]


def parse_dates(series):
    """Перетворює стовпець у datetime (пробує формати рік-місяць-день та день-місяць-рік)."""
    normal = pd.to_datetime(series, errors="coerce")
    day_first = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return day_first if day_first.isna().sum() < normal.isna().sum() else normal


def load_data(filename, year):
    """Завантажує файл, залишає дані за потрібний рік, Date - індекс."""
    try:
        df = read_file(filename)
    except FileNotFoundError:
        print(f"Помилка: файл {filename} не знайдено! "
              "Завантажте його зі сторінки donnees.montreal.ca.")
        return None
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        print(f"Помилка відкриття або читання файлу {filename}: {error}")
        return None

    if df is None or df.empty:
        print(f"Помилка: файл {filename} порожній.")
        return None

    date_column = find_date_column(df)
    df[date_column] = parse_dates(df[date_column])
    df = df.dropna(subset=[date_column]).set_index(date_column).sort_index()
    df.index.name = "Date"

    df = df[df.index.year == year]
    if df.empty:
        print(f"Помилка: у файлі немає даних за {year} рік.")
        return None

    # залишаємо лише числові стовпці (велодоріжки)
    df = df.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
    if df.empty:
        print("Помилка: у файлі немає числових стовпців з кількістю велосипедистів.")
        return None
    return df


# 2. Первинний аналіз
def primary_analysis(df):
    """print(df.head()), print(df.info()), print(df.describe())."""
    print_title("Перші рядки DataFrame (df.head()):")
    print(df.head())

    print_title("Інформація про DataFrame (df.info()):")
    df.info()

    print_title("Описова статистика (df.describe()):")
    print(df.describe())


# 3. Оброблення даних
def total_cyclists(df):
    """Загальна кількість велосипедистів за рік по кожній велодоріжці та всього."""
    per_track = df.sum().astype(int).sort_values(ascending=False)
    return per_track, int(per_track.sum())


def popular_months(monthly, tracks):
    """Для кожної велодоріжки визначає місяць з найбільшою кількістю велосипедистів."""
    result = []
    for track in tracks:
        month = int(monthly[track].idxmax())
        result.append((track, MONTHS[month - 1], int(monthly[track].max())))
    return result


def track_dynamics(monthly, track):
    """Динаміка використання велодоріжки за місяцями (зміна до попереднього місяця)."""
    dynamics = pd.DataFrame({
        "Month": [MONTHS[month - 1] for month in monthly.index],
        "Cyclists": monthly[track].astype(int).values,
    })
    dynamics["Change"] = dynamics["Cyclists"].diff()
    dynamics["Change_%"] = (dynamics["Cyclists"].pct_change() * 100).round(1)
    dynamics = dynamics.replace([float("inf"), float("-inf")], pd.NA)
    return dynamics


# 4. Введення користувача та графік
def ask_track(tracks, default):
    """Запитує назву велодоріжки для графіка; Enter - значення за замовчуванням."""
    lookup = {str(name).lower(): name for name in tracks}
    print("\nДоступні велодоріжки:", ", ".join(map(str, tracks)))
    while True:
        text = input(f"Введіть велодоріжку для графіка (Enter - {default}): ").strip()
        if not text:
            return default
        if text.lower() in lookup:
            return lookup[text.lower()]
        print(f"Помилка: велодоріжки \"{text}\" немає у даних.")


def plot_track(monthly, track):
    """Графік зміни кількості велосипедистів на велодоріжці за місяцями."""
    labels = [MONTHS_SHORT[month - 1] for month in monthly.index]

    plt.figure(figsize=(10, 5))
    plt.plot(labels, monthly[track].values, marker="o", color="tab:blue")
    plt.title(f"Number of cyclists by month, {YEAR}: {track}", fontsize=14)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Number of cyclists", fontsize=12)
    plt.grid(True)
    try:
        plt.savefig(PLOT_FILE, dpi=150, bbox_inches="tight")
        print(f"Графік збережено у файл {PLOT_FILE}")
    except OSError as error:
        print(f"Помилка збереження файлу {PLOT_FILE}: {error}")
    plt.show()


# Головна функція
def main():
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    df = load_data(DATA_FILE, YEAR)
    if df is None:
        return

    primary_analysis(df)

    per_track, total = total_cyclists(df)
    print_title(f"Кількість велосипедистів за {YEAR} рік по велодоріжках:")
    print(per_track)
    print(f"\nЗагальна кількість велосипедистів за {YEAR} рік: {total}")

    monthly = df.groupby(df.index.month).sum()
    top_tracks = per_track.head(TOP_TRACKS).index.tolist()

    print_title(f"Найпопулярніший місяць для {len(top_tracks)} велодоріжок:")
    for track, month, count in popular_months(monthly, top_tracks):
        print(f"{track}: {month} ({count} велосипедистів)")

    track = ask_track(list(df.columns), top_tracks[0])
    print_title(f"Динаміка використання велодоріжки {track} за місяцями:")
    print(track_dynamics(monthly, track))

    plot_track(monthly, track)


if __name__ == "__main__":
    main()