# astrojobs

Repository for astronomy degree and job related data. Based largely on Metcalfe 2008, PASP, 120, 229-234.
http://iopscience.iop.org/article/10.1086/528878

TL;DR version: jobregister\_data.csv is a document with all AAS job register data from 
January 2002 through (currently) May 2016.

Scripts:
- search_jobregister.py: requires BeautifulSoup for crawling and scraping.
    If docrawl=True, produces jobregister\_urls.txt.
    If doscrape=True, gather information from each URL in the job register archive.
    Save in groups of 100 as .pkl files.
    Read in all the .pkl files and create jobregister\_data.csv for further analysis.
    Not particularly well set up to add incrementally.
    Not necessary to rerun to use analysis; the .txt and .csv files are in the repo.
- plot\_jobregister.py: produce some summary tables and plots.

Tables and Sources:
- Produced by search\_jobregister.py:
    - jobregister\_urls.txt 
    - jobregister\_data.csv
- Update manually:
    - degrees.txt: Estimates of astronomy PhDs produced per year via 3 sources, based on Metcalfe 2008 Table 1.
    - Metcalfe2008_Table2.txt: To add yearly job register data from 1984-2002.
    - funding.txt: Need to add this.

Notes on Job Categories: In 2008, the job categorization changed. 
Here is how I combine the eight pre-2008 categories with the eight post-2008 categories into six new categories.

| Old Categories                             | New Categories                                   | This Work |
|--------------------------------------------|--------------------------------------------------|-----------|
| TT (Tenure-Track)                          | Faculty Positions (tenure and tenure-track)      | TT        |
| PostV (Postdoc) & Rsrch (Research)         | Post-doctoral Positions and Fellowships          | PV        |
| Non-Tenure Track (NTT)  & Visit (Visiting) | Faculty Positions (visiting and non-tenure)      | NTT       |
| MngOth & Other                             | Science Management & Other                       | MO        |
| RsrchSp (Research Support)                 | Science Engineering & Scientific/Technical Staff | RS        |
|                                            | Pre-doctoral/Graduate Positions                  | G         |

This is not a perfect split, especially with matching the previous Research category, though 
by eyeing through a few of those categorized as "Research," they seem to be along the lines of Postdocs.