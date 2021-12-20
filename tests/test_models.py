import pytest

from services import models


def test_creation_valid_url():
    root, ext = 'https://example.com', 'testing/'
    url = '/'.join([root, ext])
    page = models.Page(url)
    assert page.url == url
    assert page.root == root


def test_loaded_flag_success():
    page = models.Page('https://example.com/')
    assert not page.loaded
    page.load()
    assert page.loaded


def test_loaded_flag_failure():
    page = models.Page('bad-url')
    assert not page.loaded

    with pytest.raises(AttributeError):
        page.load()
    assert not page.loaded


def test_page_equality():
    page_a = models.Page('https://example.com')
    page_b = models.Page('https://example.com/')
    assert page_a == page_b


def test_page_inequality():
    page_a = models.Page('https://foo.com')
    page_b = models.Page('https://bar.com')
    assert page_a != page_b


def test_page_inequality_bad_types():
    page_a = models.Page('https://foo.com')
    page_b = 'https://bar.com'
    assert page_a != page_b


def test_page_set_inclusion():
    page_a = models.Page('https://foo.com')
    page_b = models.Page('https://bar.com')
    pages = [page_a]
    assert page_a in pages
    assert page_b not in pages
