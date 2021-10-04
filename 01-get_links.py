# GET THE LIST OF urls FOR ALL astro-ph PAPERS ON arXiv FOR A GIVEN year
import os
import argparse
import datetime
from web_scraping_fn import *


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

    with open(path, 'a') as ofile:
        for href in href_new:
            ofile.write(f'{href}\n')

    _end = datetime.datetime.now()
    _diff = _end - _start
    print(f'FILE WRITTEN:\t{args.year}\t{len(href_new)}\t'
          f'{datetime.timedelta(seconds=_diff.seconds, microseconds=_diff.microseconds)} sec')
