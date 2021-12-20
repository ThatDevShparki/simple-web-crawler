import json

import pytest

from services import models


def test_creation_valid_url():
    url = 'https://example.com/'
    page = models.Page(url)
    assert page.url == url


def test_loaded_flag_success():
    page = models.Page('https://example.com/')
    assert not page.loaded
    page.load()
    assert page.loaded


def test_serialize_loaded_flag():
    page = models.Page('https://example.com/')
    assert not page.loaded
    models.Page.serialize(page)
    assert page.loaded


def test_to_json_loaded_flag():
    page = models.Page('https://example.com/')
    assert not page.loaded
    page.to_json()
    assert page.loaded


def test_iter_links_not_loaded_error():
    page = models.Page('https://example.com/')
    assert not page.loaded
    with pytest.raises(AttributeError):
        list(page.iter_links())


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


def test_page_iter_links():
    page = models.Page('https://example.com/')
    page.load()
    links = [models.Page('https://www.iana.org/domains/example')]
    for link in links:
        link.load()
    assert list(page.iter_links()) == links


# Portability tests
def test_page_serialization():
    url = 'https://example.com/'
    doc = {
        'page_url': url,
        'title': 'Example Domain',
        'level': 0,
        'links': ['https://www.iana.org/domains/example'],
        'images': [],
    }
    page = models.Page(url)
    page.load()
    assert json.dumps(
        models.Page.serialize(page), sort_keys=True
    ) == json.dumps(doc, sort_keys=True)
    assert json.dumps(page.to_json(), sort_keys=True) == json.dumps(
        models.Page.serialize(page), sort_keys=True
    )


def test_page_deserialization():
    url = 'https://example.com/'
    doc = {
        'page_url': url,
        'title': 'Example Domain',
        'level': 0,
        'links': ['https://www.iana.org/domains/example'],
        'images': [],
    }
    assert models.Page.deserialize(doc) == models.Page(url)


# Forward and backward compability
def test_page_forward_portability():
    url = 'https://example.com/'
    page = models.Page(url)

    assert models.Page.deserialize(models.Page.serialize(page)) == page


def test_page_backward_portability():
    url = 'https://example.com/'
    doc = {
        'page_url': url,
        'title': 'Example Domain',
        'level': 0,
        'links': ['https://www.iana.org/domains/example'],
        'images': [],
    }

    assert json.dumps(
        models.Page.serialize(models.Page.deserialize(doc)), indent=2
    ) == json.dumps(doc, indent=2)
