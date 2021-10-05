import os
import datetime
import requests
from bs4 import BeautifulSoup


class Article:
    def __init__(self, paper_url=None):
        self.url = paper_url
        self.title = None
        self.date = None
        self.authors = None
        self.abstract = None
        self.subjects = None
        self.get_summary()

    def get_summary(self):
        __html = requests.get(self.url).text
        __soup = BeautifulSoup(__html, 'lxml')
        __content = __soup.find('div', {'id': 'content-inner'})
        self.title = __content.find('h1', class_='title mathjax').text.lstrip('Title:')
        self.authors = __content.find('div', class_='authors').text.lstrip('Authors:').split(',')
        self.abstract = __content.find('blockquote', class_='abstract mathjax').text.lstrip('\nAbstract: ')
        __date = __content.find('div', class_='dateline').text.split('(')[0].split('on ')[1][:-1]
        self.date = datetime.datetime.strptime(__date, "%d %b %Y").date()
        __summary = __content.find('table', {'summary': 'Additional metadata'})
        self.subjects = __summary.find('td', class_='tablecell subjects').text.lstrip('\n').split(';')


_start = datetime.datetime.now()
path = 'arxiv_astro-ph_all.dat'
if os.path.isfile(path):
    with open(path, 'r') as ifile:
        hrefs = ifile.read().splitlines()

for href in hrefs[:100]:
    paper = Article(href)
_end = datetime.datetime.now()
_diff = _end-_start
_start = _end
print(f'Time = {datetime.timedelta(seconds=_diff.seconds,microseconds=_diff.microseconds)} sec')
