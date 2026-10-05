
import json

# Параметри програми
JSON_FILE = "people.json"               # файл із повним словником
RESULT_FILE = "search_result.json"      # назва файлу з результатами за замовчуванням
FORBIDDEN_CHARS = '<>:"/\\|?*'
GENDERS = ("ч", "ж")

# Словник із практичної роботи 3
people = {
    "Коваленко Іван": [182, "ч"],
    "Шевченко Марія": [165, "ж"],
    "Бондаренко Олег": [178, "ч"],
    "Ткаченко Ольга": [170, "ж"],
    "Мельник Андрій": [190, "ч"],
    "Кравчук Наталія": [160, "ж"],
    "Савченко Петро": [175, "ч"],
    "Романюк Софія": [168, "ж"],
    "Гриценко Максим": [185, "ч"],
    "Поліщук Ірина": [172, "ж"],
}


# Перетворення та робота з JSON
def to_json_structure(data):
    """Перетворює {ім'я: [зріст, стать]} у {ім'я: {"зріст": ..., "стать": ...}}."""
    return {name: {"зріст": height, "стать": gender}
            for name, (height, gender) in data.items()}


def save_to_json(data, filename):
    """Перетворює словник у JSON і зберігає у файл."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(to_json_structure(data), file, ensure_ascii=False, indent=4)
    except OSError as error:
        print(f"Помилка запису файлу {filename}: {error}")
        return False
    print(f"Створено файл {filename}")
    return True


def print_json_file(filename, title):
    """Читає JSON-файл і виводить його вміст на екран."""
    print(f"\n{title}")
    print("-" * 40)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено!")
        return
    except json.JSONDecodeError:
        print(f"Файл {filename} містить некоректний JSON.")
        return
    except OSError as error:
        print(f"Помилка відкриття файлу {filename}: {error}")
        return
    print(json.dumps(content, ensure_ascii=False, indent=4))


# Введення та перевірка даних користувача
def ask_field():
    """Запитує, за яким полем виконувати пошук."""
    fields = {"1": "прізвище та ім'я", "2": "стать", "3": "зріст"}
    while True:
        print("\nПошук за полем:")
        for key, name in fields.items():
            print(f"  {key} - {name}")
        choice = input("Виберіть поле (1-3): ").strip()
        if choice in fields:
            return choice
        print("Помилка: введіть 1, 2 або 3.")


def ask_name():
    """Запитує прізвище/ім'я (або їх частину); порожній рядок не приймається."""
    while True:
        text = input("Введіть прізвище або ім'я (або частину): ").strip()
        if text:
            return text
        print("Помилка: запит не може бути порожнім.")


def ask_gender():
    """Запитує стать: ч або ж."""
    while True:
        gender = input("Введіть стать (ч/ж): ").strip().lower()
        if gender in GENDERS:
            return gender
        print("Помилка: стать має бути 'ч' або 'ж'.")


def ask_height():
    """Запитує мінімальний зріст (додатне ціле число)."""
    while True:
        text = input("Показати осіб зростом не менше (см): ").strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Помилка: введіть додатне ціле число.")


def ask_filename(prompt, default):
    """Запитує назву файлу; Enter - значення за замовчуванням. Додає .json."""
    while True:
        name = input(prompt).strip()
        if not name:
            return default
        if any(char in name for char in FORBIDDEN_CHARS):
            print(f"Помилка: назва не повинна містити символи {FORBIDDEN_CHARS}")
            continue
        if not name.lower().endswith(".json"):
            name += ".json"
        return name


# Пошук
def search_by_name(data, text):
    """Записи, в яких прізвище та ім'я містять заданий текст."""
    text = text.lower()
    return {name: value for name, value in data.items() if text in name.lower()}


def search_by_gender(data, gender):
    """Записи із заданою статтю."""
    return {name: value for name, value in data.items() if value[1] == gender}


def search_by_height(data, min_height):
    """Записи, де зріст не менший за заданий."""
    return {name: value for name, value in data.items() if value[0] >= min_height}


def run_search(data, field):
    """Запитує параметр пошуку відповідно до поля і виконує пошук."""
    if field == "1":
        return search_by_name(data, ask_name())
    if field == "2":
        return search_by_gender(data, ask_gender())
    return search_by_height(data, ask_height())


# Головна функція
def main():
    if not people:
        print("Помилка: словник порожній, немає даних для збереження.")
        return

    if not save_to_json(people, JSON_FILE):
        return
    print_json_file(JSON_FILE, "Зміст JSON-файлу зі словником:")

    field = ask_field()
    result = run_search(people, field)

    if not result:
        print("\nЗа вказаним запитом нічого не знайдено.")
        return

    print(f"\nЗнайдено записів: {len(result)}")
    result_name = ask_filename(
        f"Введіть назву файлу для результатів (Enter - {RESULT_FILE}): ", RESULT_FILE)

    if save_to_json(result, result_name):
        print_json_file(result_name, "Зміст файлу з результатами пошуку:")


if __name__ == "__main__":
    main()