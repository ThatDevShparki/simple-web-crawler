from __future__ import annotations

import logging
import typing as t

from bs4 import BeautifulSoup
import requests
import tldextract
from hyperlink import URL


# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Page:
    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def url(self) -> str:
        return self._url.to_text()

    def __init__(self, url: str):
        self._url = URL.from_text(url).normalize()
        self._loaded = False
        # TODO: Add validation for url: edge case with root if url is invalid
        self.root = (
            f'https://{".".join(d for d in tldextract.extract(url) if d)}'
        )

        # Placeholders for `load()`
        self.title = None
        self.content = None
        self.soup = None
        self.images = []

    def __repr__(self):
        return f'Page(url={self.url})'

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other: Page):
        if not isinstance(other, Page):
            return False
        return self.url == other.url

    def load(self):
        logger.info('Visiting %s', self.url)
        self.content = requests.get(self.url).content
        self.soup = BeautifulSoup(
            self.content, 'html.parser', from_encoding='iso-8859-1'
        )
        self.title = self.soup.title.text

        # Load all images on page
        for ele in self.soup.find_all('img'):
            link = self.resolve(ele.attrs.get('src'))
            if link not in self.images:
                self.images.append(link)

        self._loaded = True

    def iter_links(self):
        visited = []
        for ele in self.soup.find_all('a'):
            link = self.resolve(ele.attrs.get('href'))
            if link not in visited:
                visited.append(link)
                yield Page(link)

    def resolve(self, url: str) -> str:
        return self._url.click(url).normalize().to_text()

    # Portablility
    @classmethod
    def serialize(cls, page: Page) -> dict:
        if not page.loaded:
            page.load()

        return {
            'page_url': page.url,
            'links': list(p.url for p in page.iter_links()),
            'images': page.images,
        }

    @classmethod
    def deserialize(cls, data: dict) -> Page:
        return Page(data.get('page_url'))
