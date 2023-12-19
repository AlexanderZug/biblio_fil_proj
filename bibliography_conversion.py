import re

author_regex = re.compile(r'^([\w\.]+\s[\w\.]+)')
title_regex = re.compile(r'\.\s([\w\s\.,–]+)\s//')
journal_regex = re.compile(r'\/\/\s*([^/]+)\.\s*(\d{4})')
year_regex = re.compile(r'(\d{4})\.')
issue_regex = re.compile(r'No\s*(\d+)\.')
pages_regex = re.compile(r'С\.\s([\w\s\.,–]+)\.')



class ArticleConverter:
    def __init__(self, article):
        self.author = author_regex.search(article)
        self.title = title_regex.search(article)
        self.journal = journal_regex.search(article)
        self.year = year_regex.search(article)
        self.issue = issue_regex.search(article)
        self.pages = pages_regex.search(article)

    def get_translation(self):
        return f"{self.issue.group(1)}"

