import os
from web_scraping_fn import *



# url TO THE MAIN PAGE OF NEW PAPERS
url = 'https://arxiv.org/list/astro-ph/recent'

# EXTEND THE PAGE TO ALL RECENT PAPERS
url = get_all(url)
html = requests.get(url).text
soup = BeautifulSoup(html, 'lxml')

# LOAD THE EXISTING RECORD
path = 'arxiv_astro-ph_all.dat'
href_papers = []
if os.path.isfile(path):
    with open(path, 'r') as ifile:
        href_papers = ifile.read().splitlines()

# GET THE NEW ENTRIES
href_new = get_papers(url, href_papers)

if len(href_new) > 0:
    with open(path, 'a') as ofile:
        for href in href_new:
            ofile.write(f'{href}\n')

print(len(href_papers), len(href_new))
