import re
from googletrans import Translator
from transliterate import translit


class ArticleConverter:
    AUTHOR_REGEX = re.compile(r"^([\w\.]+\s[\w\.]+)")
    TITLE_REGEX = re.compile(r"\.\s([\w\s\.,–]+)\s//")
    JOURNAL_REGEX = re.compile(r"\/\/\s*([^/]+)\.\s*(\d{4})")
    YEAR_REGEX = re.compile(r"(\d{4})\.")
    ISSUE_REGEX = re.compile(r"(?:No|№)\s*(\d+)\.")
    PAGES_REGEX = re.compile(r'С\.\s([\w\s\.,–-]+)\.')

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

            result_str = f"{author} \"{title_trans}\" [{title_en}], {journal}, {self.year.group(1)}, № {self.issue.group(1)}, pp. {self.pages.group(1)}. (In Russian)"

            return result_str
        except AttributeError as e:
            # Handle attribute errors (e.g., if a regex pattern does not match)
            return f"Error: {e}"
