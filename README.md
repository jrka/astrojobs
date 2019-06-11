# astrojobs

Repository for astronomy degree and job related data. Based largely on Metcalfe 2008, PASP, 120, 229-234.
http://iopscience.iop.org/article/10.1086/528878

TL;DR version: jobregister\_table.csv is a document with all AAS job register data from
January 2002 through May 2016. jobregister\_table\_2019.csv includes June 2016 
through May 2019. 
Informative plots, including supplementary data,
are available here: https://github.com/jrka/astrojobs/blob/master/jobregister_plots.pdf

To Add, Ways to Contribute:
- Any way to get astro-specific thesis counts from UMI database? Online support told me you cannot anymore.

Notes on Job Categories:
- In 2008, the job categorization changed.
- Here is how I combine the eight pre-2008 categories with the eight post-2008 categories into six new categories.

| Old Categories                             | New Categories                                   | This Work |
|--------------------------------------------|--------------------------------------------------|-----------|
| TT (Tenure-Track)                          | Faculty Positions (tenure and tenure-track)      | TT        |
| PostV (Postdoc) & Rsrch (Research)         | Post-doctoral Positions and Fellowships          | PV        |
| Non-Tenure Track (NTT)  & Visit (Visiting) | Faculty Positions (visiting and non-tenure)      | NTT       |
| MngOth & Other                             | Science Management & Other                       | MO        |
| RsrchSp (Research Support)                 | Science Engineering & Scientific/Technical Staff | RS        |
|                                            | Pre-doctoral/Graduate Positions                  | G         |

- This is not a perfect split, especially with matching the previous Research category, though
by eyeing through a few of those categorized as "Research," they seem to be along the lines of Postdocs.

Notes on Institution Type:
- The academic years 2016-2018 (June 2016 - May 2019) include the country listed in the job ad. 
- Many job ads with foreign countries are not listed in the Foreign category. 
- Some of the plots re-categorize these jobs to distinguish those that are US-only.

Scripts:
- (OLD) search_jobregister.py: requires BeautifulSoup for crawling and scraping.
    If docrawl=True, produces jobregister\_urls.txt.
    If doscrape=True, gather information from each URL in the job register archive.
    Save in groups of 100 as .pkl files.
    Read in all the .pkl files and create jobregister\_table.csv for further analysis.
    Not particularly well set up to add incrementally.
    Not necessary to rerun to use analysis; the .txt and .csv files are in the repo.
    The AAS job register website has changed, and this no longer works.
- search\_jobregister\_2019.py: like above, but updated for new job register website.
    Hard-coded to search a certain date range. 
- plot\_jobregister.py: produce some summary tables (see below) and plots (jobregister\_plots.pdf). Requires pandas.

Tables Included:
- Produced by search\_jobregister.py:
    - jobregister\_urls.txt
    - jobregister\_table.csv
- Produced by search\_jobregister\_2019.py:
    - jobregister\_urls\_2019.txt
    - jobregister\_table\_2019.csv
- Update manually:
    - degrees.txt: Estimates of astronomy PhDs produced per year via 3 sources, 
    based on Metcalfe 2008 Table 1.
    - Metcalfe2008\_Table2.txt: To add yearly job register data from 1984-2002.
    - funding.txt: Total astronomy, NASA, and NSF research-only obligations by year, 
    in actual dollar amounts, based on Metcalfe 2008 Table 1.
    - funding\_deflators.txt: Deflators to convert actual dollar amounts to real 
    (currently, 2009) dollars. 
- Produced by plot\_jobregister.py:
    - jobregister\_categories\_byyear.csv: Number of jobs in each category (see note) by year.
    - jobregister\_instclass\_byyear.csv: Number of jobs in each institution class by year.
    - Similarly named plots with \_USonly suffix include only those jobs that are 
    both a) NOT listed as Foreign (2003 and beyond distinction) and 
    b) NOT listed with a foreign country in the "Country" field" (2016 and beyond distinction).
