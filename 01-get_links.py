# GET THE LIST OF urls FOR ALL astro-ph PAPERS ON arXiv FOR A GIVEN year
import os
import argparse
import requests
from bs4 import BeautifulSoup

import datetime


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
            url_all = 'https://arxiv.org' + _href.get('href')
            break
    return url_all


def get_months(year):
    """
    :param year: year for which to search the records -> int
    :return: list of url's for the months of this year -> list[str]
    """
    year_url = 'https://arxiv.org/year/astro-ph/'+str(year)[-2:]
    href_month = []
    html = requests.get(year_url).text
    soup = BeautifulSoup(html, 'lxml')
    # GET ALLS LISTS li FROM WHICH TO EXTRACT THE LINKS TO EACH MONTH
    lis = soup.find_all('li')
    for li in lis:
        _hrefs = li.find_all('a')
        for _href in _hrefs:
            if str(year)[-2:] in _href.text:
                href_month.append(get_all('https://arxiv.org' + _href.get('href')))
    return href_month


def get_papers(url_month, href_stored):
    """
    :param url_month: url to the list of all paper for this month
    :param href_stored: links already stored
    :return: list of url's for all papers of this month -> list[str]
    """
    html = requests.get(url_month).text
    soup = BeautifulSoup(html, 'lxml')
    dts = soup.find_all('dt')
    url_papers = []
    for dt in dts:
        _url = 'https://arxiv.org' + dt.find('a', {'title': 'Abstract'}).get('href')
        if _url not in href_stored:
            url_papers.append(_url)
    return url_papers


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int)  # year for which to retrieve the info
    args = parser.parse_args()

    # GET THE LINKS ALREADY SAVED
    path = 'arxiv_astro-ph_all.dat'
    href_papers = []
    if os.path.isfile(path):
        with open(path, 'r') as ifile:
            href_papers = ifile.read().splitlines()

    # GET THE LISTS OF LINKS TO ALL PAPERS FROM YEAR=year
    _start = datetime.datetime.now()
    href_new = []
    href_months = get_months(args.year)
    for href in href_months:
        href_new.extend(get_papers(href, href_papers))
    _end = datetime.datetime.now()
    _diff = _end-_start

    with open(path, 'a') as ofile:
        for href in href_new:
            ofile.write(f'{href}\n')

    print(f'{args.year}\t{len(href_new)}\t'
          f'{datetime.timedelta(seconds=_diff.seconds, microseconds=_diff.microseconds)} sec')
