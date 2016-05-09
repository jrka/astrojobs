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

Tables and Sources:
- Produced by scripts:
-- jobregister\_urls.txt
-- jobregister\_data.csv
- Update manually:
-- degrees.txt: Estimates of astronomy PhDs produced per year via 3 sources, based on Metcalfe 2007 Table 1.
-- funding.txt: To add.


Notes on Job Categories: In 2008, the job categorization changed. 
Here are the eight pre-2008 categories, as described by the 2004-2005 AAS Annual Report:
- Postdoc (PostV): Fellowships and other semi-permanent postdoctoral positions.
- Tenure-Track (TT): Academic appointments which are tenured or tenured-track.
- Non-Tenure Track (NTT): Academic appointments which are not tenured or tenure-track.
- Research (Rsrch): Positions in which research is the primary focus.
- Research Support (RsrchSp): Positions in which the majority of the work is at the direction of another.
- Visiting (Visit): A temporary position at a particular institution, typically a teaching position.
- Management (MngOth): Positions which are administrative or managerial in focus.
- Other (Other): Also includes positions which do not fit into the other categories.

And these are the eight post-2008 categories. Postings in 2008 had both.
- 'Faculty Positions (tenure and tenure-track)'
- 'Science Engineering'
- 'Scientific/Technical Staff'
- 'Pre-doctoral/Graduate Positions'
- 'Other'
- 'Science Management'
- 'Post-doctoral Positions and Fellowships'
- 'Faculty Positions (visiting and non-tenure)'