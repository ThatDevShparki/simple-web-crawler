import os
import json
from pathlib import Path
import multiprocessing as mp

import requests
from bs4 import BeautifulSoup, element
from urllib.parse import urlparse

# from services import models


def main():
    url = 'https://www.martinfowler.com/bliki/'
    queue, tree = [url], {}
    while queue:
        current = queue.pop(0)
        if current in tree:
            continue

        tree[current] = {'links': [], 'images': []}
        soup = BeautifulSoup(
            requests.get(current).content,
            'html.parser',
            from_encoding='iso-8859-1',
        )

        for element in soup.find_all('a'):
            link = element.attrs.get('href')
            if link:
                if link.startswith('/'):
                    link = url + link[1:]
                tree[current]['links'].append(link)

                if link.startswith(url) and link not in tree:
                    queue.append(link)

        print(json.dumps(tree[current], indent=2))

    outputs_path = Path('outputs/sitetree.json').resolve()
    os.makedirs(outputs_path.parent, exist_ok=True)
    with open(outputs_path, mode='w', encoding='utf-8') as buffer:
        json.dump(tree, buffer, indent=2)
