import re
import datetime
import requests
from bs4 import BeautifulSoup


def get_all(url_month):
    """
    :param url_month: Expand the records to include all papers for this month
    :return: url to the full list of papers for this month -> str
    """
    html = requests.get(url_month).text
    soup = BeautifulSoup(html, 'lxml')

    url_all = url_month

    # GET TO THE FULL LIST FOR THAT YEAR-MONTH
    for _href in soup.find_all('a'):
        # IF MULTIPLE PAGES THEN GET THE LIST OF 'all' PAPERS OTHERWISE KEEP THE ORIGINAL LINK
        if _href.text == 'all':
            url_all = 'https://export.arxiv.org' + _href.get('href')
            break
    return url_all


def get_months(year):
    """
    :param year: year for which to search the records -> int
    :return: list of url's for the months of this year -> list[str]
    """
    year_url = 'https://export.arxiv.org/year/astro-ph/'+str(year)[-2:]
    href_month = []
    html = requests.get(year_url).text
    soup = BeautifulSoup(html, 'lxml')
    # GET ALLS LISTS li FROM WHICH TO EXTRACT THE LINKS TO EACH MONTH
    lis = soup.find_all('li')
    for li in lis:
        _hrefs = li.find_all('a')
        for _href in _hrefs:
            if str(year)[-2:] in _href.text:
                href_month.append(get_all('https://export.arxiv.org' + _href.get('href')))
    return href_month


def get_papers(url_month):
    """
    :param url_month: url to the list of all paper for this month
    :return: list of url's for all papers of this month -> list[str]
    """
    html = requests.get(url_month).text
    soup = BeautifulSoup(html, 'lxml')
    dts = soup.find_all('dt')
    url_papers = []
    for dt in dts:
        if not isinstance(dt.find('a', {'title': 'Abstract'}), type(None)):
            _url = 'https://export.arxiv.org' + dt.find('a', {'title': 'Abstract'}).get('href')
            url_papers.append(_url)
    return url_papers


class Article:
    def __init__(self, title=None, date=None, authors=None, abstract=None,
                 keywords=None, citations=None, references=None, url_paper=None):
        """
        :param url_paper: arXiv url to the paper -> str
        Given the arXiv url retrieve the paper summary from NASA ADS if available otherwise get it from arXiv
        """
        self.url = url_paper
        self.__html = requests.get(self.url)
        self.__soup = BeautifulSoup(self.__html.content, 'lxml')

        self.title = title
        self.date = date
        self.authors = authors
        self.abstract = abstract
        self.keywords = keywords
        self.citations = citations
        self.references = references

        self.get_date()

        # if self.is_ads():
        #    self.get_summary_ads()
        # else:
        self.get_summary_arxiv()

    def to_dict(self):
        my_dict = {'title': self.title,
                   'date': self.date,
                   'authors': self.authors,
                   'abstract': self.abstract,
                   'keywords': self.keywords,
                   'citations': self.citations,
                   'references': self.references}
        return my_dict

    def get_date(self):
        """
        :return: None -> Fill-in the self.date from arXiv
        """
        __date = self.__soup.find('div', class_='dateline').text
        __date = str(re.findall('(\d{1,} \S{3} \d{4})+', __date)[0])
        self.date = datetime.datetime.strptime(__date, "%d %b %Y").date()

    def is_ads(self):
        """
        :return: True if ADS url available, False if not -> bool
        """
        __ads_url = self.__soup.find('a', string='NASA ADS').get('href')
        return not isinstance(__ads_url, type(None))

    def get_summary_arxiv(self):
        """
        :return: None -> Get the paper summary from arXiv
        """
        __content = self.__soup.find('div', class_='leftcolumn')
        self.title = __content.find('h1', class_='title mathjax').text.lstrip('Title:').lstrip()
        self.authors = [author.lstrip().lstrip('\n') for author in
                        __content.find('div', class_='authors').text.lstrip('Authors:').split(',')]
        self.abstract = __content.find('blockquote', class_='abstract mathjax').text.lstrip('\nAbstract: ')
        __summary = __content.find('table', {'summary': 'Additional metadata'})
        self.keywords = __summary.find('td', class_='tablecell subjects').text.lstrip('\n').split(';')

    def get_summary_ads(self):
        """
        :return: None -> Get the paper summary from NASA ADS
        """
        __ads_url = self.__soup.find('a', class_='abs-button abs-button-small cite-ads').get('href')
        __html = requests.get(__ads_url).text
        __soup = BeautifulSoup(__html, 'lxml')
        self.title = ' '.join(__soup.find('h2', class_='s-abstract-title').text.split())
        __authors = __soup.find_all('li', class_='author')
        self.authors = []
        for author in __authors:
            self.authors.append(author.text.rstrip('\n'))
        self.abstract = ' '.join(__soup.find('div', class_='s-abstract-text').text.lstrip('\nAbstract').split())
        self.keywords = __soup.find('dt', text='Keywords:').find_next('dd').text.strip().split('\n')
        self.keywords = [_keyword.rstrip(';') for _keyword in self.keywords]
        self.citations = __soup.find('a', {'data-widget-id': 'ShowCitations'})
        if not isinstance(self.citations, type(None)):
            self.citations = int(self.citations.find('span', class_='num-items').text.lstrip('(').rstrip(')'))
        self.references = __soup.find('a', {'data-widget-id': 'ShowReferences'})
        if not isinstance(self.references, type(None)):
            self.references = int(self.references.find('span', class_='num-items').text.lstrip('(').rstrip(')'))
