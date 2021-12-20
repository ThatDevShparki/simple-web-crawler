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

from services.models import Page


# Logging setup
logging.basicConfig(filename='logs/output.log', level=logging.INFO)


@click.command()
@click.option('-url', required=True, help='The URL to crawl.')
@click.option(
    '--depth', type=int, default=None, help='The maximumd depth to traverse.'
)
def crawl(url: str, depth: int = None):
    root = Page(url)
    queue, tree = [root], {}

    while queue:
        current = queue.pop()
        tree[current.url] = current.to_json()
        print(json.dumps(current.to_json(), indent=2))

        for page in current.iter_links():
            if all(
                [
                    page.url.startswith(url),
                    page.url not in tree,
                    (depth is None or page.level <= depth),
                ]
            ):
                queue.append(page)

    outputs_path = Path('outputs/sitetree.json').resolve()
    os.makedirs(outputs_path.parent, exist_ok=True)
    with open(outputs_path, mode='w', encoding='utf-8') as buffer:
        json.dump(tree, buffer, indent=2)


if __name__ == '__main__':
    crawl()  # pylint: disable=no-value-for-parameter
