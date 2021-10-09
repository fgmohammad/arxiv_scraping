# Web Scraper for arXiv

## Requirements  
requests  
bs4  


## 01-get_links.py 
Gets urls to all papers for a given year



## Usage 
<li>Get the all papers in the year=year (yyyy format)<br />
`$ python get_records_by_year.py --year year`

<li>Get recent entries each day (recommended: schedule to run once a day, using e.g. crontab)
`$ python get_recent_entries.py`
