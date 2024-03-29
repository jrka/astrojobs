from bs4 import BeautifulSoup
import urllib
import re
import numpy as np
import pandas as pd
import pickle as pickle
import glob

# Major changes from 2019 script (8/6/22)
# - Save everything to new .csv and .pkl files with "2019_extrafields" in file name; refers to 
#   this new search done in 2019_extrafields, but job ad data is from June 2019 through May 2019_extrafields. 
# - This illustrates that my coding is weaksauce and someone could easily make 
#   the script more general. 
# - Uh I finally updated my python from 2.x to 3.x, which means:
# 		- changed calls from e.g. print year, month to print(year,month)
#   	- Likewise changed cPickle to pickle. 
#   	-  urllib.urlopen to urllib.request.urlopen
# - Getting HTTP Error 403: Forbidden error. The URL string is still correct. 
#   Fix is based on: https://stackoverflow.com/questions/16627227/problem-http-error-403-in-python-3-web-scraping
# - pickle error,TypeError: write() argument must be str, not bytes, "w" to "wb"
# - Encoding character change for the Country field.
#
# Additional changes 8/18/22
# - Add any fields having to do with Pay Compensation.
#     They are: salary min, salary max, hourly rate min, hourly rate max, stipend, compensation notes
#     Also Benefits
# - Create two versions of the resulting .csv file:
#   One with the job text, pay compensation, or benefits.
#   One without (usual)
# Example with hourly: https://jobregister.aas.org/ad/8b8e13de
# Example with salary: https://jobregister.aas.org/ad/3af94175
# Example with stipend: view-source:https://jobregister.aas.org/ad/27fc0021

# MAKING THIS FOR 2019, on 3/24/23
# I copied the 2019_extrafields file to get extra fields, but I replaced the dates with 
# those from the 2019 file.

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"
    
opener=AppURLopener()

#-------------
# Select if you'd like to do the crawling (get all relevant URLs)
# and/or the scraping (get the contents of those HTML files)

# The crawling produces jobregister_urls_new.txt, which is needed for scraping.
# If you already have jobregister_urls_new.txt, no need to crawl, will just read
# the contents of that file instead. This is included in the github repo but
# of course can be updated.
docrawl=True

# The scraping loops through all the URLs in the aforementioned file and 
# grabs the relevant field information. These are saved in .pkl files in 
# batches of 100 job postings, because the connection is sometimes lost.
# This allows you to restart at a given point in the list without having to 
# redo the entire thing.
doscrape=True

#------
    
######### GET A LIST OF ALL JOB POSTINGS
if docrawl:
	# Modifications from previous: manually input the years, months to collect.
	# Though only 12 months appear on https://jobregister.aas.org/jobs/archive,
	# the previous links are available. Individual job links seem to work back 
	# through January 2017; January 2016's links don't work. But June 2016 works,
	# and I left off in May 2016, so perfect timing!
    yearlist=['2016','2017','2018','2019']
    #archive='https://jobregister.aas.org/jobs/archive'
    #r=urllib.urlopen(archive).read()
    #archivesoup = BeautifulSoup(r)

    # To get all links
    #monthlist=archivesoup.find_all('a')
    #monthlist=[x.get('href') for x in monthlist]
    #monthlist=[x for x in monthlist if 'year=' in x]
    alllist=[]
    for year in yearlist: 
        if year=='2016':
            monthlist=['06','07','08','09','10','11','12']
        elif year=='2019':
            monthlist=['01','02','03','04','05']
        else:
            monthlist=['01','02','03','04','05','06','07','08','09','10','11','12']
        for month in monthlist:
            print(year, month)     
            print('https://jobregister.aas.org/jobs/archive/'+year+'/'+month)
            r=opener.open('https://jobregister.aas.org/jobs/archive/'+year+'/'+month).read()
            #r=urllib.request.urlopen('https://jobregister.aas.org/jobs/archive/'+year+'/'+month).read()
            monthsoup = BeautifulSoup(r)
            jlist=monthsoup.find_all('a')
            jlist=[x.get('href') for x in jlist]
            #jlist=[x for x in jlist if 'JobID=' in x]
            jlist=[x for x in filter(None,jlist) if '/ad/' in x]
            alllist.append(jlist)
            
    # Flatten List
    alllist=[item for sublist in alllist for item in sublist]
    # Remove Duplicates in List
    newlist=list(set(alllist))
    # Print to a file
    with open('jobregister_urls_2019_extrafields.txt','w') as f:
        for item in newlist:
            f.write("%s\n" % item)
else:
    with open('jobregister_urls_2019_extrafields.txt') as f:
        newlist=f.read().splitlines()
    
#-------------

# Scraping Setup
# The fields we want from the HTML
fields=['field-name-field-publish-date',
        'field-name-field-archive-date',
        'field-name-field-application-deadline',
        'field-name-field-job-category', 
        'field-name-field-institution-company',
        'field-name-field-institution-classification',
        'field-type-text-with-summary', # The main text
        'title',
        'field-name-field-location-country',
        'field-name-field-salary-min',# Add more 8/16/22
        'field-name-field-salary-max',
        'field-name-field-hourly-rate-min',
        'field-name-field-hourly-rate-max',
        'field-name-field-stipend',
        'field-name-field-benefits',
        'field-name-field-location-zip-postal'] # Added 11/27/22

# Shortened dictionary names for the above.
fields_dict=['post','archive','deadline','category','inst','instclass','text','title','country',
    'salary-min','salary-max','hourly-min','hourly-max','stipend','benefits','postalcode']

# Start and end strings to find the contents of those fields above.
start=[r'datatype="xsd:dateTime" property="dc:date">',
       'datatype="xsd:dateTime" property="dc:date">',
       'datatype="xsd:dateTime" property="dc:date">',
       'Job Category: </div><div class="field-items"><div class="field-item even">',
       'Institution/Company: </div><div class="field-items"><div class="field-item even">',
       'Institution Classification/Type: </div><div class="field-items"><div class="field-item even">',
       'Job Announcement Text: </div><div class="field-items"><div class="field-item even" property="content:encoded">',
       '<h1 class="title" id="page-title">',
       #'Country:\xc2\xa0</div><div class="field-items"><div class="field-item even">']
       'Country:\xa0</div><div class="field-items"><div class="field-item even">',
       'Salary Min:\xa0</div><div class="field-items"><div class="field-item even">',
       'Salary Max:\xa0</div><div class="field-items"><div class="field-item even">',
       'Hourly Rate Min:\xa0</div><div class="field-items"><div class="field-item even">',
       'Hourly Rate Max:\xa0</div><div class="field-items"><div class="field-item even">',
       'Stipend:\xa0</div><div class="field-items"><div class="field-item even">',
       'Included Benefits:\xa0</div><div class="field-items"><div class="field-item even">',
       'Zip/Postal:\xa0</div><div class="field-items"><div class="field-item even">']
end=['</span>','</span>','</span>','</div></div></div>','</div></div></div>',
    '</div></div></div>','</div></div></div>','</h1>','</div></div></div>', # Ends w/ country
    '</div></div></div>','</div></div></div>','</div></div></div>','</div></div></div>',
    '</div></div></div>','</div></div></div>','</div></div></div>']
        
######### SCRAPE ALL JOB ADS FOR INFO, SAVE PERIODICALLY IN GROUPS OF 100
# Sometimes the connection is lost; you can restart using startind as a multiple of 100
# For example, if the last .pkl file you have in your folder is 'alljobs_04500to04599.pkl',
# that means you should use startind=4600 and rerun to start from there.
if doscrape:
    data=[]
    startind=0 # Make it a multiple of 100.
    for u, url in enumerate(newlist[startind:]): # For each listing in the job register...
        r=opener.open('http://jobregister.aas.org/'+url[1:]).read() # open contents
        soup = BeautifulSoup(r)
        
        # Create dictionary to fill in 
        d={}
        d['url']=url
        d['i']=u+startind # Index corresponding to our list of URLs
        for i,f in enumerate(fields):
            if f=='field-type-text-with-summary':
                try: # I am not sure why this is as such. 
                    s=str(soup.find_all("div",class_=f)[0])
                    result=s
                except:
                    result=''
            elif f=='field-name-field-benefits':
                try: # I am not sure why this is as such. 
                    s=str(soup.find_all("div",class_=f)[0])
                    result=s.partition(start[i])[2].partition(end[i])[0]
                except:
                    result=''
            elif f=='title':
                s=str(soup.find_all("h1",class_="title")[0])
                result=s.split('>')[1].split('<')[0]
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
            print(u+startind+1,'of',len(newlist))
            # We're either in a group of 100, or at the end of our list.
            if (u+startind!=len(newlist)-1):
                ind1=u-99 
            else:
                ind1=u-np.mod(len(newlist)-1,100) # Don't go back a full 99 if just at end of list.
            pfile='alljobs2019_extrafields_'+str(data[ind1]['i']).zfill(5)+'to'+str(u+startind).zfill(5)+'.pkl'
            print(pfile)
            if (u+startind!=len(newlist)-1): # In retrospect, this is not necessary to split up.
                pickle.dump(data[ind1:u+1],open(pfile,"wb"))
            else:
                pickle.dump(data[ind1:],open(pfile,"wb"))
    
# Read in and combine all our pickles.
pickles=glob.glob('./alljobs2019_extrafields_*to*.pkl')
# Put them in order
pickles.sort()
data=[]
for i, f in enumerate(pickles):
    tmp=pickle.load(open(f,"rb"))
    inds=[x['i'] for x in tmp]
    data.append(tmp)
    print(i,f,np.min(inds),np.max(inds),len(tmp))
    #print len(tmp),len(data),[len(sublist) for sublist in data]
# Flatten
data=[item for sublist in data for item in sublist]
# Make this a pandas dataframe
df=pd.DataFrame(data)
print(len(df),len(set(df.url)),len(set(newlist)))

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
#df.to_csv('./jobregister_table_2019_extrafields.csv',
#    columns=['i','year','month','acyear','title','category','inst','instclass','url','country','postalcode'])
    
# Added 8/16/22 with all the rest of the fields.
df.to_csv('./jobregister_table_2019_extrafields.csv')
