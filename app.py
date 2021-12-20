"""Entry-point for all scripts."""
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
    '--depth', type=int, default=None, help='The maximum depth to traverse.'
)
@click.option(
    '--output',
    default='outputs/sitetree.json',
    help='The output path to save the sitetree.',
)
def crawl(url: str, depth: int, output: str):
    """Crawl a webpage URL with an optional max depth of DEPTH."""
    root = Page(url)
    queue, tree = [root], {}

    while queue:
        current = queue.pop(0)
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

    outputs_path = Path(output).resolve()
    os.makedirs(outputs_path.parent, exist_ok=True)
    with open(outputs_path, mode='w', encoding='utf-8') as buffer:
        json.dump(tree, buffer, indent=2)


if __name__ == '__main__':
    crawl()  # pylint: disable=no-value-for-parameter
