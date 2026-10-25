import pandas as pd

# Параметри програми
INPUT_FILE = "life_expectancy_extended.csv"
RESULTS_FILE = "analysis_results.csv"  # результати групування
PROCESSED_FILE = "processed_data.csv"  # оброблені та відсортовані дані
DELIMITER = ";"

FILTER_YEAR = 2015  # умова фільтрації: рік не раніше
FILTER_LIFE = 73  # та тривалість життя більша за

# назви стовпців у файлі -> короткі назви для аналізу
COLUMN_NAMES = {
    "Country Name": "Country",
    "Country Code": "Code",
    "Year": "Year",
    "Life expectancy at birth, total (years)": "Life_expectancy",
    "Population, total": "Population",
    "GDP per capita (current US$)": "GDP_per_capita",
}
NUMERIC_COLUMNS = ["Year", "Life_expectancy", "Population", "GDP_per_capita"]


def print_title(text):
    """Виводить заголовок розділу."""
    print(f"\n{text}")
    print("-" * 60)


# 1. Завантаження даних
def load_data(filename):
    """Завантажує CSV у DataFrame і перейменовує стовпці."""
    try:
        df = pd.read_csv(filename, sep=DELIMITER, encoding="utf-8-sig")
        print("Файл успішно завантажено")
    except FileNotFoundError:
        print(f"Помилка: файл {filename} не знайдено! "
              "Спершу запустіть task1_extend_data.py")
        return None
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        print(f"Помилка читання файлу {filename}: {error}")
        return None

    if df.empty or not set(COLUMN_NAMES).issubset(df.columns):
        print(f"Помилка: у файлі {filename} немає потрібних даних або стовпців.")
        return None
    return df.rename(columns=COLUMN_NAMES)[list(COLUMN_NAMES.values())]


# 2. Базовий аналіз
def basic_analysis(df):
    """Виводить вміст DataFrame, head(3), типи, розмір і статистику."""
    print_title("Початкові дані:")
    print(df)

    print_title("Перші 3 рядки DataFrame:")
    print(df.head(3))

    print_title("Типи даних:")
    print(df.dtypes)

    print_title("Розмір DataFrame (рядків, стовпців):")
    print(df.shape)

    print_title("Описова статистика:")
    print(df.describe())


# 3. Попереднє оброблення
def convert_types(df):
    """Змінює типи даних: числові стовпці та цілі значення."""
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before = len(df)
    df = df.dropna(subset=NUMERIC_COLUMNS).copy()
    if len(df) < before:
        print(f"Видалено рядків з пропущеними значеннями: {before - len(df)}")

    df["Year"] = df["Year"].astype(int)
    df["Population"] = df["Population"].astype("int64")
    return df


def add_calculated_column(df):
    """Додає розрахунковий стовпець: ВВП країни = ВВП на особу * населення."""
    df["GDP_total_bln_USD"] = (
            df["GDP_per_capita"] * df["Population"] / 1e9
    ).round(2)
    return df


def filter_data(df):
    """Фільтрація: рік не раніше FILTER_YEAR і тривалість життя > FILTER_LIFE."""
    return df[(df["Year"] >= FILTER_YEAR) & (df["Life_expectancy"] > FILTER_LIFE)]


def sort_data(df):
    """Сортування за тривалістю життя (за спаданням)."""
    return df.sort_values(by="Life_expectancy", ascending=False)


# 4. Групування та агрегація
def group_data(df):
    """Групування за країною: середні, максимальні, мінімальні значення."""
    return df.groupby("Country").agg(
        Life_exp_mean=("Life_expectancy", "mean"),
        Life_exp_max=("Life_expectancy", "max"),
        Life_exp_min=("Life_expectancy", "min"),
        GDP_per_capita_mean=("GDP_per_capita", "mean"),
        Population_mean=("Population", "mean"),
        Years_count=("Year", "nunique"),
    ).round(2)


# 5. Збереження результатів
def save_csv(df, filename, with_index=False, index_label=None):
    """Зберігає DataFrame у CSV-файл."""
    try:
        df.to_csv(filename, sep=DELIMITER, index=with_index,
                  index_label=index_label, encoding="utf-8-sig")
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"Створено файл {filename}")
    return True


# Головна функція
def main():
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)

    df = load_data(INPUT_FILE)
    if df is None:
        return

    basic_analysis(df)

    df = convert_types(df)
    print_title("Типи даних після перетворення:")
    print(df.dtypes)

    df = add_calculated_column(df)
    print_title("DataFrame з новим показником (GDP_total_bln_USD):")
    print(df)

    filtered_df = filter_data(df)
    print_title(f"Результат фільтрації (Year >= {FILTER_YEAR}, "
                f"Life_expectancy > {FILTER_LIFE}):")
    if filtered_df.empty:
        print("За заданою умовою записів не знайдено.")
    else:
        print(filtered_df)

    sorted_df = sort_data(df)
    print_title("Результат сортування за Life_expectancy (за спаданням):")
    print(sorted_df)

    grouped_df = group_data(df)
    print_title("Результат групування за країною:")
    print(grouped_df)

    print_title("Кількість унікальних значень:")
    print(f"Країн: {df['Country'].nunique()} ({', '.join(df['Country'].unique())})")
    print(f"Років: {df['Year'].nunique()}")

    print()
    save_csv(grouped_df, RESULTS_FILE, with_index=True, index_label="Country")
    save_csv(sorted_df, PROCESSED_FILE)


if __name__ == "__main__":
    main()