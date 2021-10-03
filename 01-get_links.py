# GET THE LIST OF urls FOR ALL astro-ph PAPERS ON arXiv FOR A GIVEN year
import argparse
import requests
from bs4 import BeautifulSoup




def get_year(year, url):
    """
    :param year: Year to be searched from the archive
    :param url: url to the main page of the historical archive
    :return: url to the records for this 'year' -> 'str'
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    _hrefs = soup.find_all('a')
    for href in _hrefs:
        if href.text == str(year):
            return 'https://arxiv.org' + href.get('href')

def get_all(url_month):
    """
    :param url_month: Expand the records to include all papers for this month
    :return: url to the full list of papers for this month -> str
    """
    html = requests.get(url_month).text
    soup = BeautifulSoup(html, 'lxml')

    url_all = url_month

    # GET TO THE FULL LIST FOR THAT YEAR-MONTH
    for href in soup.find_all('a'):
        # IF MULTIPLE PAGES THEN GET THE LIST OF 'all' PAPERS OTHERWISE KEEP THE ORIGINAL LINK
        if href.text == 'all':
            url_all = 'https://arxiv.org' + href.get('href')
    return url_all

def get_months (year, url):
    """
    :param year: year for which to search the records
    :return: list of url's for the months of this year
    """
    year_url = get_year(year, url)
    href_month = []
    html = requests.get(year_url).text
    soup = BeautifulSoup(html, 'lxml')
    # GET ALLS LISTS li FROM WHICH TO EXTRACT THE LINKS TO EACH MONTH
    lis = soup.find_all('li')
    for li in lis:
        _hrefs = li.find_all('a')
        for href in _hrefs:
            if str(year)[-2:] in href.text:
                href_month.append(get_all('https://arxiv.org' + href.get('href')))
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
        url_papers.append('https://arxiv.org' + dt.find('a', {'title': 'Abstract'}).get('href'))
    return (url_papers)






if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int)  # year for which to retrieve the info
    args = parser.parse_args()

    # GET THE LISTS OF LINKS TO ALL PAPERS FROM YEAR=year
    url = 'https://arxiv.org/archive/astro-ph'

    href_papers = []

    href_months = get_months(args.year, url)
    for href in href_months:
        href_papers.extend(get_papers(href))
    print (len(href_papers))
