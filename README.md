# astrojobs

Repository for astronomy degree and job related data.

Scripts:
- search_jobregister.py: requires BeautifulSoup for crawling and scraping.
    If docrawl=True, produces jobregister\_urls.txt.
    If doscrape=True, gather information from each URL in the job register archive.
    Save in groups of 100 as .pkl files.
    Read in all the .pkl files and create jobregister\_data.csv for further analysis.
    Not particularly well set up to add incrementally.
    Not necessary to rerun to use analysis; the .txt and .csv files are in the repo.
- plot\_jobregister.py

Tables and Sources:
- Produced by search\_jobregister.py:
    - jobregister\_urls.txt 
    - jobregister\_data.csv
- Update manually:
    - degrees.txt: Estimates of astronomy PhDs produced per year via 3 sources, based on Metcalfe 2007 Table 1.
    - Metcalfe2007_Table2.txt: To add yearly job register data from 1984-2002.
    - funding.txt: To add.

Notes on Job Categories: In 2008, the job categorization changed. 
Here is how I combine the eight pre-2008 categories with the eight post-2008 categories into 6.

| Old Categories                             | New Categories                                   | This Work |
|--------------------------------------------|--------------------------------------------------|-----------|
| TT (Tenure-Track)                          | Faculty Positions (tenure and tenure-track)      | TT        |
| PostV (Postdoc) & Rsrch (Research)         | Post-doctoral Positions and Fellowships          | PV        |
| Non-Tenure Track (NTT)  & Visit (Visiting) | Faculty Positions (visiting and non-tenure)      | NTT       |
| MngOth & Other                             | Science Management & Other                       | MO        |
| RsrchSp (Research Support)                 | Science Engineering & Scientific/Technical Staff | RS        |
|                                            | Pre-doctoral/Graduate Positions                  | G         |

This is not a perfect split, especially with matching the previous Research category.