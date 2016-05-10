import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Read in the .csv file as a pandas dataframe 
df=pd.read_csv('./jobregister_table.csv')
# Only choose academic year 2003 and 2014, which are complete as of May 2016
df=df[df.acyear>=2003]
df=df[df.acyear<=2014]

# Also read in the degree information by year
deg=pd.read_csv('./degrees.txt',comment='#',delim_whitespace=True,na_values='...')
deg=deg.rename(columns={'Year':'acyear'})
deg=deg.set_index('acyear')
# Add Metcalfe2008_Table2 to fill out 1984-2002. Don't need 2003 and beyond.
m07t2=pd.read_csv('./Metcalfe2008_Table2.txt',comment='#',delim_whitespace=True,na_values='...')
m07t2=m07t2[m07t2.Year<2003]
m07t2=m07t2.rename(columns={'Year':'acyear','NT':'NTT','R':'Rsrch','RS':'RS'})
m07t2=m07t2.set_index('acyear')
# We are combining PV with Rsrch.
m07t2['PV']=m07t2['PV']+m07t2['Rsrch']
del m07t2['Rsrch']
del m07t2['F']

###### SETUP PLOTTING PARAMETERS
pdffile='./jobregister_plots.pdf'
pdf=PdfPages(pdffile)
# We have 8 categories for institution class, use colorbrewer2.org, 8-class Set1
color8=['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf']

##### STANDARDIZE TEXT FOR CATEGORIES
# Check out the available categories each year. Note 2008 is the "crossover" year.
for yr in set(df.year):
    cats=set(df[df.year==yr]['category'])
    print yr,len(cats)
    print cats    
    
# Combine these as such:
df.category[np.any([df.category=='TT',df.category=='Faculty Positions (tenure and tenure-track)'],axis=0)]='TT'
df.category[np.any([df.category=='PostV',df.category=='Rsrch',df.category=='Post-doctoral Positions and Fellowships',],axis=0)]='PV'
df.category[np.any([df.category=='NTT',df.category=='Visit',df.category=='Faculty Positions (visiting and non-tenure)'],axis=0)]='NTT'
df.category[np.any([df.category=='MngOth',df.category=='Other',df.category=='Science Management'],axis=0)]='MO'
df.category[np.any([df.category=='RsrchSp',df.category=='Science Engineering',df.category=='Scientific/Technical Staff',],axis=0)]='RS'
df.category[df.category=='Pre-doctoral/Graduate Positions']='G'

##### CREATE A FEW DATA TABLES
# Print a few tables
# http://stackoverflow.com/questions/34907019/pandas-histogram-by-dates-and-sorted-by-categories

###### First table: Job categories by year.
table1=df.groupby('acyear')['category'].value_counts().unstack(1)
# Add a column with "All"
table1=pd.concat([table1,pd.DataFrame(table1.sum(axis=1),columns=['All'])],axis=1)
table1=pd.concat([m07t2,table1],axis=0,join='outer')
table1.to_csv('./jobregister_categories_byyear.csv')

# Plot total data here. Matches Metcalfe 2008 Figure 3, jobs per year
plt.clf()
plt.plot(table1.index,table1['All'],label='All Jobs',color='k')
plt.plot(table1.index,table1['TT'],label='Tenure-Track',color='green')
plt.plot(table1.index,table1['PV'],label='Postdoc/Research',color='b',linestyle='dotted')
plt.plot(table1.index,table1['NTT'],label='Non-Tenure-Track',color='r',linestyle='--')
plt.plot(table1.index,table1['RS'],label='Research Support',color='cyan',linestyle='--')
plt.plot(table1.index,table1['MO'],label='Other',color='magenta',linestyle='-.')
plt.axvline(2006,color='gray')
plt.legend(loc='best')
pdf.savefig()

# Metcalfe 2008 Figure 3, job register ads / new PhDs
# Would be best to use UMI measures, but we don't have that.
table1=pd.concat([table1,deg],axis=1,join='outer')
plt.clf()
plt.plot(table1.index,table1['UMI']/table1['AIP'])
plt.plot(table1.index,table1['UMI']/table1['SED'])
useavg=np.all([table1.index>=1990,table1.index<=2006],axis=0)
avgAIP=np.average(table1['UMI'][useavg]/table1['AIP'][useavg])
avgSED=np.average(table1['UMI'][useavg]/table1['SED'][useavg])
plt.axhline(avgAIP)
plt.axhline(avgSED)
plt.legend(loc='best')

plt.clf()
plt.plot(table1.index,table1['All']/table1['UMI'],label='All Jobs',color='k')
plt.plot(table1.index,table1['All']/(table1['SED']*avgSED),label='All Jobs, SED avg')
plt.plot(table1.index,table1['All']/(table1['AIP']*avgAIP),label='All Jobs, AIP avg')
plt.legend(loc='best')
# Come back to this.
pdf.savefig()


###### Second table: Institution Class by Year
table2=df.groupby('acyear')['instclass'].value_counts().unstack(1).to_csv('./jobregister_instclass_byyear.csv')

#### PLOTS AND STATISTICS OF JUST OUR DATA
# Histogram: Postings by year, broken down by category
# Stacked
ax1=df.groupby(df.acyear)['category']\
    .value_counts()\
    .unstack(1)\
    .plot(kind='bar', stacked=True,color=color8,figsize=(11,8))
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10),
          ncol=2, fancybox=True, shadow=True,fontsize=10)
ax1.figure.subplots_adjust(bottom=0.2)
ax1.set_xlabel('Year Posted')
#pdf.savefig(ax1.figure)

# Loop for future plots...
nplot=5
for i in range(nplot):
    plt.cla()
    
    if i==0:
        group=df.groupby(df.acyear)['category']
        ytitle=''
    elif i==1: 
        group=df.groupby(df.acyear)['instclass']
        ytitle=''
    elif i==2:
        group=df.groupby('month')['year']
        ytitle=''
    elif i==3:
        group=df.groupby(df.category)['instclass']
        ytitle=''
    elif i==4: 
        group=df[df.instclass=='Foreign'].groupby(df.year)['category']
        ytitle='Foreign Only'
    
    # Stacked, then unstacked
    for stacked in [True,False]:
        plt.cla()
        ax=group.value_counts().unstack(1).plot(kind='bar',ax=ax1,color=color8,
            stacked=stacked,figsize=(11,8))
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10),
              ncol=3, fancybox=True, shadow=True,fontsize=10)
        ax.set_ylabel(ytitle)
        pdf.savefig(ax.figure)
    
    # Then stacked and percentage.
    plt.cla()
    ax=group.value_counts(normalize=True).unstack(1).plot(kind='bar',ax=ax1,color=color8,
            stacked=True,figsize=(11,8))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
              ncol=3, fancybox=True, shadow=True,fontsize=10)
    ax.set_ylabel(ytitle)      
    pdf.savefig(ax.figure)    

    # Line plot of percentage
    plt.cla()
    ax=group.value_counts(normalize=True).unstack(1).plot(kind='line',ax=ax1,color=color8,
            stacked=False,figsize=(11,8))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
              ncol=3, fancybox=True, shadow=True,fontsize=10)
    ax.set_ylabel(ytitle)
    pdf.savefig(ax.figure)    
    
# Histograms, one subplot per job type, with histogram of institutions
plt.cla()
ax=df.groupby(df.instclass)['category']\
    .value_counts().unstack(1).plot(kind='bar',ax=ax1,color=color8,subplots=True,
    layout=(2,4),legend=False,figsize=(11,8),sharex=True)
pdf.savefig(ax[0][0].figure)

# close PDF
pdf.close()

# Months
df.groupby('month')['month'].value_counts()
for mo in np.arange(12)+1:
    print mo,np.sum(df.month==mo)/float(len(df))