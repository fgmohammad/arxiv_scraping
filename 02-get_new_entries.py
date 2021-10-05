import os
from web_scraping_fn import *



# url TO THE MAIN PAGE OF NEW PAPERS
url = 'https://arxiv.org/list/astro-ph/recent'

# EXTEND THE PAGE TO ALL RECENT PAPERS
url = get_all(url)
html = requests.get(url).text
soup = BeautifulSoup(html, 'lxml')

# LOAD THE EXISTING RECORD
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'arxiv_astro-ph_all.dat')
href_papers = []
if os.path.isfile(filename):
    with open(filename, 'r') as ifile:
        href_papers = ifile.read().splitlines()

# GET THE NEW ENTRIES
href_new = get_papers(url, href_papers)

if len(href_new) > 0:
    with open(filename, 'a') as ofile:
        for href in href_new:
            ofile.write(f'{href}\n')

print(len(href_papers), len(href_new))
