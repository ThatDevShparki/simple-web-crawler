import os
import json
from pathlib import Path
import multiprocessing as mp
from queue import Empty
from concurrent.futures import ThreadPoolExecutor
import logging

import click
import requests
from bs4 import BeautifulSoup, element
from urllib.parse import urlparse
import tldextract

from services.models import Page


# Logging setup
logging.basicConfig(filename='logs/output.log', level=logging.INFO)


@click.command()
@click.option('-url', required=True, help='The URL to crawl.')
@click.option('--depth', default=None, help='The maximumd depth to traverse.')
def crawl(url, depth):
    root = f'https://{".".join(d for d in tldextract.extract(url) if d)}'
    print(root)

    queue = mp.Queue()
    queue.put(url)

    def process_url(url, tree):
        _links, _images = [], []

        soup = BeautifulSoup(
            requests.get(url).content,
            'html.parser',
            from_encoding='iso-8859-1',
        )
        for ele in soup.find_all('a'):
            link = ele.attrs.get('href')
            if link:
                if not (link.startswith('http') or link.startswith('www')):
                    if not (link.startswith('/') or link.startswith('#')):
                        link = '/' + link
                    link = root + link

                if link not in _links:
                    _links.append(link)

                if link.startswith(url) and link not in tree:
                    queue.put(link)

        tree[url] = {'links': _links, 'images': _images}
        # print(json.dumps({url: tree[url]}, indent=2))

    tree, results = mp.Manager().dict(), []
    with ThreadPoolExecutor(max_workers=8) as executor:
        while queue:
            try:
                current = queue.get(timeout=2)
                print('hi')
            except Empty:
                return

            if current in tree:
                continue

            results.append(executor.submit(process_url, current, tree).result())

    outputs_path = Path('outputs/sitetree.json').resolve()
    os.makedirs(outputs_path.parent, exist_ok=True)
    with open(outputs_path, mode='w', encoding='utf-8') as buffer:
        json.dump(tree, buffer, indent=2)


if __name__ == '__main__':
    # crawl()  # pylint: disable=no-value-for-parameter

    url = 'https://martinfowler.com/bliki'
    page = Page(url)
    print(json.dumps(Page.serialize(page), indent=2))
