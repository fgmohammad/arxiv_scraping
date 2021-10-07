import os
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging


class Article:
    def __init__(self, title=None, date=None, authors=None, abstract=None,
                 keywords=None, citations=None, references=None, paper_url=None):
        """
        :param paper_url: arXiv url to the paper -> str
        Given the arXiv url retrieve the paper summary from NASA ADS if available otherwise get it from arXiv
        """
        self.url = paper_url
        print (self.url)
        self.__html = requests.get(self.url).text
        self.__soup = BeautifulSoup(self.__html, 'lxml')

        self.title = title
        self.date = date
        self.authors = authors
        self.abstract = abstract
        self.keywords = keywords
        self.citations = citations
        self.references = references

        self.get_date()

        #if self.is_ads():
        #    self.get_summary_ads()
        #else:
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
        __content = self.__soup.find('div', {'id': 'content-inner'})
        __date = __content.find('div', class_='dateline').text.split('(')[0].split('on ')[1][:-1]
        self.date = datetime.datetime.strptime(__date, "%d %b %Y").date()

    def is_ads(self):
        """
        :return: True if ADS url available, False if not -> bool
        """
        __ads_url = self.__soup.find('a', class_='abs-button abs-button-small cite-ads').get('href')
        return not isinstance(__ads_url, type(None))

    def get_summary_arxiv(self):
        """
        :return: None -> Get the paper summary from arXiv
        """
        __content = self.__soup.find('div', {'id': 'content-inner'})
        self.title = __content.find('h1', class_='title mathjax').text.lstrip('Title:')
        self.authors = __content.find('div', class_='authors').text.lstrip('Authors:').split(',')
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


if __name__ == '__main__':
    _start = datetime.datetime.now()

    # WORKING DIRECTORY
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # GET THE urls FROM THE FILE
    path = os.path.join(dir_path, 'arxiv_astro-ph_all.dat')
    if os.path.isfile(path):
        with open(path, 'r') as ifile:
            hrefs = ifile.read().splitlines()


    # CREATE A LOG FILE
    log_filename = os.path.join(dir_path, 'astro-ph_records_1992-now.log')
    logging.basicConfig(level=logging.INFO, filename=log_filename,
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    # RETRIEVE INFORMATION FOR EACH PAPER
    papers = []
    for idx, href in enumerate(hrefs[:10000]):
        papers.append(Article(paper_url=href).to_dict())
        if (idx%1000)==0:
            logging.info(f'{idx}\t{datetime.datetime.now()}')

    # CREATE A PANDAS DATAFRAME AND WRITE THE RESULT TO A .csv FILE
    df = pd.DataFrame.from_records(papers)
    filename = os.path.join(dir_path, 'astro-ph_records_1992-now.csv')
    df.to_csv(filename)

    _end = datetime.datetime.now()
    _diff = _end-_start
    _start = _end

    logging.info(f'Time = {datetime.timedelta(seconds=_diff.seconds,microseconds=_diff.microseconds)} sec')
