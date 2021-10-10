import os
import logging
import pandas as pd
import argparse
from web_scraping_fn import *


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2021)
    args = parser.parse_args()

    # GET THE PATH TO THE WORKING DIRECTORY
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # CREATE log FILE
    log_filename = os.path.join(dir_path, f'astro-ph_records_{args.year}.log')
    logging.basicConfig(level=logging.INFO, filename=log_filename,
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    # START TIMESTAMP
    _start = datetime.datetime.now()

    # GET THE url TO THE YEAR
    url_months = get_months(args.year)
    _diff = datetime.datetime.now() - _start
    _start = datetime.datetime.now()
    logging.info(f'Got url_months:'
                 f' Time = {datetime.timedelta(seconds=_diff.seconds, microseconds=_diff.microseconds)} sec')

    # LOAD THE LIST OF PAPERS ALREADY IN THE RECORD (IF SUCH A RECORD EXISTS)
    path_stored = os.path.join(dir_path, 'arxiv_astro-ph_stored.dat')
    papers_stored = []
    if os.path.isfile(path_stored):
        with open(path_stored, 'r') as ifile:
            papers_stored = ifile.read().splitlines()



    # LOOP OVER EACH MONTH TO GET urls OF ALL PAPERS IN THAT MONTH AND GET INFO FOR EACH PAPER
    papers = []
    papers_new = []
    for month, url_month in enumerate(url_months):
        url_papers = get_papers(url_month)
        for url_paper in url_papers:
            if url_paper in papers_stored:
                # IF PAPER IS ALREADY STORED -> continue TO THE NEXT PAPER
                continue
            else:
                # OTHERWISE STORE THE INFO AND ADD THE url TO THE LIST OF STORED PAPERS
                try:
                    papers.append(Article(url_paper=url_paper).to_dict())
                    papers_new.append(url_paper)
                except Exception as e:
                    logging.error(f'{url_paper} raised the error:\t{e}!!!')
        _diff = datetime.datetime.now() - _start
        _start = datetime.datetime.now()
        logging.info(f'month: {month+1:02d}, url_month: {url_month}, n_papers: {len(url_papers)},'
                     f' Time = {datetime.timedelta(seconds=_diff.seconds, microseconds=_diff.microseconds)} sec')

    # WRITE THE UPDATED LIST OF STORED PAPERS TO THE FILE
    with open(path_stored, 'a') as ofile:
        for url_paper in papers_new:
            ofile.write(f'{url_paper}\n')

    # CREATE A PANDAS DATAFRAME AND WRITE THE RESULT TO A .csv FILE
    df = pd.DataFrame.from_records(papers)
    filename = os.path.join(dir_path, f'astro-ph_records_1992-now.csv')
    if os.path.isfile(filename):
        df.to_csv(path_or_buf=filename, header=False, mode='a', index=False)
    else:
        df.to_csv(path_or_buf=filename, index=False)
    _diff = datetime.datetime.now() - _start
    _start = datetime.datetime.now()
    logging.info(f'csv Stored. Time = {datetime.timedelta(seconds=_diff.seconds, microseconds=_diff.microseconds)} sec')
