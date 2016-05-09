from bs4 import BeautifulSoup
import urllib
import re
import numpy as np
import pandas as pd
import cPickle as pickle
import glob

#-------------
# Select if you'd like to do the crawling (get all relevant URLs)
# and/or the scraping (get the contents of those HTML files)

# The crawling produces jobregister_urls.txt, which is needed for scraping.
# If you already have jobregister_urls.txt, no need to crawl, will just read
# the contents of that file instead. This is included in the github repo but
# of course can be updated.
docrawl=True

# The scraping loops through all the URLs in the aforementioned file and 
# grabs the relevant field information. These are saved in .pkl files in 
# batches of 100 job postings, because the connection is sometimes lost.
# This allows you to restart at a given point in the list without having to 
# redo the entire thing.
doscape=True

#------
    
######### GET A LIST OF ALL JOB POSTINGS
docrawl=True
if docrawl:
    archive='https://jobregister.aas.org/archives/back_issues'
    r=urllib.urlopen(archive).read()
    archivesoup = BeautifulSoup(r)

    # To get all links
    monthlist=archivesoup.find_all('a')
    monthlist=[x.get('href') for x in monthlist]
    monthlist=[x for x in monthlist if 'year=' in x]
    alllist=[]
    for month in monthlist:
            print month
            r=urllib.urlopen('https://jobregister.aas.org/archives/'+month).read()
            monthsoup = BeautifulSoup(r)
            jlist=monthsoup.find_all('a')
            jlist=[x.get('href') for x in jlist]
            jlist=[x for x in jlist if 'JobID=' in x]
            alllist.append(jlist)
            
    # Flatten List
    alllist=[item for sublist in alllist for item in sublist]
    # Remove Duplicates in List
    newlist=list(set(alllist))
    # Print to a file
    with open('jobregister_urls.txt','w') as f:
        for item in newlist:
            f.write("%s\n" % item)
else:
    with open('jobregister_urls.txt') as f:
        newlist=f.read().splitlines()
    
#-------------

# Scraping Setup
# The fields we want from the HTML
fields=['field-field-ad-post-date',
        'field-field-ad-archive-date',
        'field-field-application-deadline',
        'field-field-job-category', 
        'field-field-institution-name',
        'field-field-institution-classification',
        'field-field-job-announcement', # The main text
        'title']

# Shortened dictionary names for the above.
fields_dict=['post','archive','deadline','category','inst','instclass','text','title']

# Start and end strings to find the contents of those fields above.
start=[r'<span class="date-display-single">',
       '<span class="date-display-single">',
       '<span class="date-display-single">',
       'Job Category:\xc2\xa0</div>\r\n',
       'Institution/Company Name:\xc2\xa0</div>\r\n',
       'Institution Classification/Type:\xc2\xa0</div>\r\n',
       'Job Announcement Text:',
       '">"']
end=['</span>','</span>','</span>','</div>','</div>','</div>','</div>','</div>','</a>']
        
######### SCRAPE ALL JOB ADS FOR INFO, SAVE PERIODICALLY IN GROUPS OF 100
# Sometimes the connection is lost; you can restart using startind as a multiple of 100
# For example, if the last .pkl file you have in your folder is 'alljobs_04500to04599.pkl',
# that means you should use startind=4600 and rerun to start from there.
if doscrape:
    data=[]
    startind=8400 # Make it a multiple of 100.
    for u, url in enumerate(newlist[startind:]): # For each listing in the job register...
        r=urllib.urlopen('http://jobregister.aas.org/'+url[2:]).read() # open contents
        soup = BeautifulSoup(r)
        
        # Create dictionary to fill in 
        d={}
        d['url']=url
        d['i']=u+startind # Index corresponding to our list of URLs
        for i,f in enumerate(fields):
            if f=='field-field-job-announcement':
                try:
                    s=str(soup.find_all("div",class_=f)[0])
                    result=s
                except:
                    result=''
            elif f=='title':
                s=str(soup.find_all("h2",class_="title")[0])
                result=re.search('%s(.*)%s' % (url[-5:]+'">','</a>'), s).group(1).strip()
            else:
                try:
                    s=str(soup.find_all("div",class_=f)[0])
                    result=re.search('%s(.*)%s' % (start[i],end[i]), s).group(1).strip()
                except:
                    result=''
            d[fields_dict[i]]=result
        # Add dictionary to our list
        data.append(d)
        
        # Output progress and save as we go, because sometimes we lose connection
        if u>0 and np.mod(u+startind+1,100)==0 or (u+startind==len(newlist)-1):
            print u+startind+1,'of',len(newlist)
            # We're either in a group of 100, or at the end of our list.
            if (u+startind!=len(newlist)-1):
                ind1=u-99 
            else:
                ind1=u-np.mod(len(newlist)-1,100) # Don't go back a full 99 if just at end of list.
            pfile='alljobs_'+str(data[ind1]['i']).zfill(5)+'to'+str(u+startind).zfill(5)+'.pkl'
            print pfile
            if (u+startind!=len(newlist)-1): # In retrospect, this is not necessary to split up.
                pickle.dump(data[ind1:u+1],open(pfile,"w"))
            else:
                pickle.dump(data[ind1:],open(pfile,"w"))
    
# Read in and combine all our pickles.
pickles=glob.glob('./alljobs_*to*.pkl')
data=[]
for i, f in enumerate(pickles):
    tmp=pickle.load(open(f,"rb"))
    inds=[x['i'] for x in tmp]
    data.append(tmp)
    print i,f,np.min(inds),np.max(inds),len(tmp)
    #print len(tmp),len(data),[len(sublist) for sublist in data]
# Flatten
data=[item for sublist in data for item in sublist]
# Make this a pandas dataframe
df=pd.DataFrame(data)
print len(df),len(set(df.url)),len(set(newlist))

# Convert posting date from string to datetime.
df.post=pd.to_datetime(df.post) 
df['year']=df.post.dt.year
df['month']=df.post.dt.month

# But, what we really want is academic year, to be comparable to e.g. Metcalfe 2007.
# For acadademic year X, want June X - June X+1
#   2003 is June 2003-June 2004. January-May (inclusive) should be previous year.
df['acyear']=df['year']
df['acyear'][df['month']<=5]=df['year'].copy()-1

# Save the contents of this dataframe, except the job text, which is large (file size is ~ 10x as large)
# Also don't save the deadline or archive date. Just the posting year and month.
df.to_csv('./jobregister_table.csv',
    columns=['i','year','month','acyear','title','category','inst','instclass','url'])
