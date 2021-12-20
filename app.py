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


def _v1_crawl(url: str, depth: int):
    """Non-parallelized crawl."""
    root = Page(url)
    queue, tree = [root], {}

    while queue:
        current = queue.pop(0)
        print(current)

        tree[current.url] = current.to_json()
        for page in current.iter_links():
            if all(
                [
                    page.url.startswith(url),
                    page.url not in tree,
                    (depth is None or page.level <= depth),
                ]
            ):
                queue.append(page)

    return tree


def _v2_crawl(url: str, depth: int):
    """Super-Fast-Awesome (i.e. parallelized) crawl."""
    _MAX_CPUS = int(max(mp.cpu_count() / 2, mp.cpu_count() - 2))

    root = Page(url)
    with mp.Manager() as manager:
        queue, tree = manager.Queue(), manager.dict()
        queue.put(root)

        def iter_queue():
            while queue:
                try:
                    current = queue.get(block=True, timeout=5)
                except:
                    return

                yield current

        def process_page(page: Page):
            print(page)
            tree[page.url] = page.to_json()
            for child_page in page.iter_links():
                if all(
                    [
                        child_page.url.startswith(url),
                        child_page.url not in tree,
                        (depth is None or child_page.level <= depth),
                    ]
                ):
                    queue.put(child_page)

        with ThreadPoolExecutor(max_workers=_MAX_CPUS) as executor:
            executor.map(process_page, iter_queue())

        return tree._getvalue()  # pylint: disable=no-member,protected-access


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
@click.option(
    '--superfastawesome',
    is_flag=True,
    help='Enable this option for Super-Fast-Awesome mode (i.e. multiprocessing)!',
)
def crawl(url: str, superfastawesome: bool, depth: int, output: str):
    """Crawl a webpage URL with an optional max depth of DEPTH."""

    tree = {}
    if not superfastawesome:
        tree = _v1_crawl(url, depth)
    else:
        tree = _v2_crawl(url, depth)

    outputs_path = Path(output).resolve()
    os.makedirs(outputs_path.parent, exist_ok=True)
    with open(outputs_path, mode='w', encoding='utf-8') as buffer:
        json.dump(tree, buffer, indent=2)


if __name__ == '__main__':
    crawl()  # pylint: disable=no-value-for-parameter
