import re
from abc import ABC, abstractmethod

from googletrans import Translator
from transliterate import translit


class BibliographyConverter(ABC):
    def __init__(self, bibliography: str):
        self.bibliography = bibliography

    @abstractmethod
    def get_translation(self) -> dict[str, str]:
        pass

    @abstractmethod
    def get_transliteration(self) -> dict[str, str]:
        pass

    @abstractmethod
    def get_bibliography(self) -> str:
        pass


class Article(BibliographyConverter):
    AUTHOR_REGEX = re.compile(r"^([\w\.,–\s]+)\.")
    TITLE_REGEX = re.compile(r"\.\s(.+?)\s//")
    JOURNAL_REGEX = re.compile(r"\/\/\s*([^/\\]+)[\.:]+\s*(\d{4})")
    YEAR_REGEX = re.compile(r"(\d{4})\.")
    ISSUE_REGEX = re.compile(r"(?:No|№)\s*(\d+)\.")
    PAGES_REGEX = re.compile(r"С\.\s([\w\s\.,–\u2013-]+)\.")

    def __init__(self, article: str):
        self.author = self.AUTHOR_REGEX.search(article)
        self.title = self.TITLE_REGEX.search(article)
        self.journal = self.JOURNAL_REGEX.search(article)
        self.year = self.YEAR_REGEX.search(article)
        self.issue = self.ISSUE_REGEX.search(article)
        self.pages = self.PAGES_REGEX.search(article)

    def get_translation(self) -> dict[str, str]:
        translator = Translator()
        title_translation = translator.translate(self.title.group(1), dest="en").text

        return {"english_title": title_translation}

    def get_transliteration(self) -> dict[str, str]:
        author_translit = translit(self.author.group(1), "ru", reversed=True)
        title_translit = translit(self.title.group(1), "ru", reversed=True)
        journal_translit = translit(self.journal.group(1), "ru", reversed=True)

        return {
            "transliterated_author": author_translit,
            "transliterated_title": title_translit,
            "transliterated_journal": journal_translit,
        }

    def get_bibliography(self) -> str:
        try:
            author = self.get_transliteration().get("transliterated_author", "")
            title_en = self.get_translation().get("english_title", "")
            title_trans = self.get_transliteration().get("transliterated_title", "")
            journal = self.get_transliteration().get("transliterated_journal", "")

            result_str = f'{author} "{title_trans}" [{title_en}], {journal}, {self.year.group(1)}, № {self.issue.group(1)}, pp. {self.pages.group(1)}. (In Russian)'

            return result_str
        except AttributeError:
            return (
                "Библиография прописана некорректно. "
                "Допустимый формат: Фамилия И.О. Название статьи // Название журнала. Год. №. С. 1–10. "
                "или Фамилия И.О. Название статьи // Название журнала. Год. No. С. 1–10."
            )


class Book(BibliographyConverter):
    AUTHOR_REGEX = re.compile(r"^([^\.]+\.[^\.]+)\.")
    TITLE_REGEX = re.compile(r"\.\s*([\w\s\.,:–!?;\"\'«»„“”‘’-]+)\s*[^:]*:")
    PUBLISH_HOUSE_REGEX = re.compile(r":\s*([^0-9]+)\d{4}")
    CITY = re.compile(r"\.\s*([^:]+)\s*:")
    YEAR_REGEX = re.compile(r"\b(\d{4})\b")
    PAGES_REGEX = re.compile(r"(\d+)\s*[сc]\.")

    def __init__(self, book: str):
        self.author = self.AUTHOR_REGEX.search(book)
        self.title = self.TITLE_REGEX.search(book)
        self.publish_house = self.PUBLISH_HOUSE_REGEX.search(book)
        self.city = self.CITY.search(book)
        self.year = self.YEAR_REGEX.search(book)
        self.pages = self.PAGES_REGEX.search(book)

    def get_translation(self) -> dict[str, str]:
        translator = Translator()

        title_translation = translator.translate(
            " ".join(self.title.group(1).split()[1:-1])[:-1], dest="en"
        ).text
        city = self.city.group(1).split()[-1]
        cities = {"М.": "Moscow", "СПб.": "Saint Petersburg", "Л.": "Leningrad"}

        if city in cities:
            city_translation = cities[city]
        else:
            city_translation = translator.translate(city, dest="en").text

        return {
            "english_title": title_translation,
            "english_city": city_translation,
        }

    def get_transliteration(self) -> dict[str, str]:
        author_translit = translit(self.author.group(1), "ru", reversed=True)
        title_translit = translit(
            " ".join(self.title.group(1).split()[1:-1])[:-1], "ru", reversed=True
        )
        publish_house_translit = translit(
            self.publish_house.group(1), "ru", reversed=True
        )

        return {
            "transliterated_author": author_translit,
            "transliterated_title": title_translit,
            "transliterated_publish_house": publish_house_translit,
        }

    def get_bibliography(self) -> str:
        try:
            author = self.get_transliteration().get("transliterated_author", "")
            title_en = self.get_translation().get("english_title", "")
            title_translit = self.get_transliteration().get("transliterated_title", "")
            city = self.get_translation().get("english_city", "")
            publish_house = self.get_transliteration().get(
                "transliterated_publish_house", ""
            )

            result_str = f"{author}. {title_translit} [{title_en}]. {city}: {publish_house} {self.year.group(1)}. {self.pages.group(1)} pp. (In Russian)"

            return result_str
        except AttributeError:
            return (
                "Библиография прописана некорректно. "
                "Допустимый формат: Фамилия И.О. Название книги. Город: Издательство, Год. 100 c. "
                "В настоящий момент рекомендуется избегать употребления двоеточия - : - в названии монографии."
            )
