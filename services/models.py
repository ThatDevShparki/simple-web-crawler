from __future__ import annotations

import logging
import typing as t
from dataclasses import dataclass, field

import bs4
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# class Page:
#     def __init__(self, url: str):
#         self.url = url
#         content = ''
#         try:
#             content = requests.get(url).content
#         except Exception as error:
#             logging.error('There was an error loading %s', url)
#         self.soup = bs4.BeautifulSoup(content)
