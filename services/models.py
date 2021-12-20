"""Models module for all object models."""
from __future__ import annotations

import logging
import typing as t

import requests
from bs4 import BeautifulSoup
from hyperlink import URL


# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Page:
    """Core model for all page objects.

    The Page container model contains most logic required to parse a page's
    content and read all links and images from it. The purpose of this class
    is to centralize all the core logic for these operations, void of any
    specific implementation or usage details.

    Note
    ----
    `title`, `content`, `soup`, and `links` all require the Page object to
    be loaded before they can be accessed reliably.

    ``` python
    page = Page('https://example.com/')
    page.load()
    ... # Rest of stuff
    ```

    The `level` attribute is used to help with filtering outside of the Page
    class. This attribute doesn't really serve a purpose within the context of
    the service-level logic but is an elegant solution to the depth filtering
    problem.

    Attributes
    ----------
    loaded : bool
        `True` if the page has been loaded, otherwise `False`.
    url : str
        The normalized URL for the page object.
    level : int
        An abstract level for which this page appears in a larger tree.
    title : str
        The page title.
    content : str
        The page contents.
    soup : BeautifulSoup
        The page contents as BeautifulSoup.
    images : list[str]
        A complete list of page images.

    """

    @property
    def loaded(self) -> bool:
        """The page loaded property."""
        return self._loaded

    @property
    def url(self) -> str:
        """The page url as a string."""
        return self._url.to_text()

    @property
    def level(self) -> int:
        """An abstract level for which this page appears in a larger tree."""
        return self._level

    def __init__(self, url: str, level: int = 0):
        self._url = URL.from_text(url).normalize()
        self._loaded = False
        self._level = level

        # Placeholders for `load()`
        self.title = None
        self.content = None
        self.soup = None
        self.images = []

    def __repr__(self):
        return f'Page(url={self.url}, level={self.level})'

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other: Page):
        if not isinstance(other, Page):
            return False
        return self.url == other.url

    def load(self):
        """Load the page and retrieve its contents.

        Calling this method, will set the `title`, `content`, `soup`, and
        `images` attributes for the page.

        Raises
        ------
        AttributeError
            Raises an AttributeError when the url cannot be accessed.

        """
        logger.info('Visiting %s', self.url)
        try:
            self.content = requests.get(self.url).content
        except Exception as error:
            self._loaded = False
            raise AttributeError(
                f'Could not visit {self.url} due to {error}.'
            ) from None

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

    def iter_links(self) -> t.Iterable[Page]:
        """Iterate through all child pages and return Page instance for each.

        Will iterate through all child pages and return a Page instance for
        each if that page has not been visited already.

        Note
        ----
        Access to child pages requires that the page have been loaded before.

        Yields
        ------
        Page
            Yields a Page object for each link found on the page.

        Raises
        ------
        AttributeError
            Raises an AttributeError when the page has not been loaded before
            accessing the iterable.

        """
        if not self._loaded:
            raise AttributeError('Page has not been loaded.')

        visited = []
        for ele in self.soup.find_all('a'):
            link = self.resolve(ele.attrs.get('href'))
            if link not in visited:
                visited.append(link)
                yield Page(link, level=self.level + 1)

    def resolve(self, url: str) -> str:
        """Resolve a url against the root url.

        Parameters
        ----------
        url : str
            The url to resolve as a string.

        Returns
        -------
        str
            Returns the resolved url as text.

        """
        return self._url.click(url).normalize().to_text()

    def to_json(self) -> dict:
        """Serialize to a JSON object as a python dictionary.

        Returns
        -------
        dict
            Returns the serialized JSON object for the Page as a python dict.

        """
        return Page.serialize(self)

    # Portablility
    @classmethod
    def serialize(cls, page: Page) -> dict:
        """Serialize a Page object to a JSON object as a python dict.

        Note
        ----
        This method will load the page if it has not already been loaded!!

        Parameters
        ----------
        page : Page
            A valid page object to serialize.

        Returns
        -------
        dict
            A python dictionary representing the Page object attributes.

        """
        if not page.loaded:
            page.load()

        return {
            'page_url': page.url,
            'title': page.title,
            'links': list(p.url for p in page.iter_links()),
            'images': page.images,
        }

    @classmethod
    def deserialize(cls, data: dict) -> Page:
        """Deserialize a python dict into a valid Page object.

        Parameters
        ----------
        data : dict
            A valid python dictionary, with a `page_url` attribute.

        Returns
        -------
        Page
            Returns a Page object from the data.

        """
        return Page(data.get('page_url'))
