import string

import matplotlib.pyplot as plt
import nltk
from nltk.corpus import gutenberg, stopwords
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer

# Параметри програми
TEXT_FILE = "melville-moby_dick.txt"  # текст за варіантом 13
LANGUAGE = "english"  # мова списку стоп-слів
TOP_N = 10  # кількість найпоширеніших слів

RAW_CHART_FILE = "top_words_raw.png"
CLEAN_CHART_FILE = "top_words_clean.png"

# ресурси NLTK: назва -> шлях до даних
RESOURCES = {
    "gutenberg": "corpora/gutenberg",
    "stopwords": "corpora/stopwords",
    "wordnet": "corpora/wordnet",
}


def print_title(text):
    """Виводить заголовок розділу."""
    print(f"\n{text}")
    print("-" * 60)


# 0. Підготовка ресурсів NLTK
def ensure_resources():
    """Перевіряє наявність ресурсів NLTK і завантажує відсутні."""
    for name, path in RESOURCES.items():
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"Завантаження ресурсу NLTK: {name} ...")
            try:
                if not nltk.download(name, quiet=True):
                    print(f"Помилка: не вдалося завантажити ресурс {name}. "
                          "Перевірте підключення до інтернету.")
                    return False
            except (OSError, ValueError) as error:
                print(f"Помилка завантаження ресурсу {name}: {error}")
                return False
    return True


# 1. Завантаження тексту та підрахунок слів
def load_words(filename):
    """Завантажує текст із колекції Project Gutenberg (список токенів)."""
    try:
        return list(gutenberg.words(filename))
    except (LookupError, OSError, ValueError) as error:
        print(f"Помилка завантаження тексту {filename}: {error}")
        return None


def count_words(words, label):
    """Виводить кількість слів і унікальних слів та порівнює їх."""
    total = len(words)
    unique = len(set(words))
    print(f"{label}")
    print(f"  Кількість слів: {total}")
    print(f"  Кількість унікальних слів: {unique}")
    if unique:
        print(f"  Відношення: слів у {total / unique:.1f} разу більше, "
              f"ніж унікальних ({unique / total * 100:.1f}% унікальних)")


# 2. Найбільш уживані слова та діаграми
def top_words(words, n):
    """Повертає n найбільш уживаних слів."""
    return FreqDist(words).most_common(n)


def print_top(top):
    """Виводить список найпоширеніших слів."""
    for rank, (word, count) in enumerate(top, start=1):
        print(f"{rank:>2}. {word:<12} {count}")


def plot_top(top, title, filename):
    """Стовпчаста діаграма найбільш уживаних слів."""
    labels = [word for word, _ in top]
    counts = [count for _, count in top]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, counts, color="tab:blue")
    plt.bar_label(bars, fontsize=9)
    plt.title(title, fontsize=14)
    plt.xlabel("Word", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(True, axis="y")
    try:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Діаграму збережено у файл {filename}")
    except OSError as error:
        print(f"Помилка збереження файлу {filename}: {error}")
    plt.show()


# 3. Видалення стоп-слів і пунктуації
def clean_words(words):
    """Переводить у нижній регістр, прибирає пунктуацію, не-слова та стоп-слова."""
    table = str.maketrans("", "", string.punctuation)
    stop_words = set(stopwords.words(LANGUAGE))

    stripped = [word.translate(table).lower() for word in words]
    return [word for word in stripped
            if word.isalpha() and word not in stop_words]


# 4. Лематизація
def lemmatize_words(words):
    """Лематизація слів (кожне унікальне слово обробляється один раз)."""
    lemmatizer = WordNetLemmatizer()
    lemma_of = {word: lemmatizer.lemmatize(word) for word in set(words)}
    return [lemma_of[word] for word in words]


# Головна функція
def main():
    if not ensure_resources():
        return

    words = load_words(TEXT_FILE)
    if not words:
        return

    print_title(f"Текст: {TEXT_FILE}")
    count_words(words, "Початковий текст (разом із пунктуацією):")

    top_raw = top_words(words, TOP_N)
    print_title(f"{TOP_N} найбільш вживаних слів:")
    print_top(top_raw)
    plot_top(top_raw, f"Top {TOP_N} words in {TEXT_FILE}", RAW_CHART_FILE)

    cleaned = clean_words(words)
    if not cleaned:
        print("Після очищення тексту слів не залишилось.")
        return

    print_title("Текст після видалення стоп-слів і пунктуації:")
    print(cleaned[:20])
    count_words(cleaned, "Після очищення:")

    top_clean = top_words(cleaned, TOP_N)
    print_title(f"{TOP_N} найбільш вживаних слів після очищення:")
    print_top(top_clean)
    plot_top(top_clean,
             f"Top {TOP_N} words without stop words and punctuation",
             CLEAN_CHART_FILE)

    lemmas = lemmatize_words(cleaned)
    count_words(lemmas, "\nПісля лематизації:")

    top_lemmas = top_words(lemmas, TOP_N)
    print_title(f"{TOP_N} найбільш вживаних слів після лематизації:")
    print_top(top_lemmas)


if __name__ == "__main__":
    main()