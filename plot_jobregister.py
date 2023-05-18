import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# 2020-08-06: Add 2019-2022 data. Had to explicitly state encoding of 2019 table.
# Update print calls for python 3.x.
# 2019-06-10: Major updates. Combine original job table with new
# one collected in 2019. Read in funding data.

# Read in the .csv file as a pandas dataframe
# Combine the three separate tables.
df = pd.read_csv('./jobregister_table.csv')
df['country']='unknown'
df.set_index('i')
df2= pd.read_csv('./jobregister_table_2019.csv',encoding="iso-8859-1")
df2['i']+=len(df)
df2.set_index('i')
df=df.append(df2,sort=False)
df.reset_index(drop=True)
# Add June 2019 - May 2022 Data
df3 = pd.read_csv('./jobregister_table_2022.csv')
df3['i']+=len(df)
df3.set_index('i')
df=df.append(df3,sort=False)
df.reset_index(drop=True)
# Only choose academic years between 2003 and 2021 (inclusive), which are
# complete as of data collected in August 2022. 
df = df[df.acyear >= 2003]
df = df[df.acyear <= 2022]

# Read in the additional tables.
# Read in the degree information by year
deg = pd.read_csv('./degrees.txt', comment='#',
                  delim_whitespace=True, na_values='...')
deg = deg.rename(columns={'Year': 'acyear'})
deg = deg.set_index('acyear')
# Add Metcalfe2008_Table2 to fill out 1984-2002. Don't need 2003 and beyond.
m07t2 = pd.read_csv('./Metcalfe2008_Table2.txt', comment='#',
                    delim_whitespace=True, na_values='...')
m07t2 = m07t2[m07t2.Year < 2003]
m07t2 = m07t2.rename(
    columns={'Year': 'acyear', 'NT': 'NTT', 'R': 'Rsrch', 'RS': 'RS'})
m07t2 = m07t2.set_index('acyear')
# We are combining PV with Rsrch.
m07t2['PV'] = m07t2['PV'] + m07t2['Rsrch']
del m07t2['Rsrch']
del m07t2['F']
# 2019 read in the funding tables.
fund = pd.read_csv('./funding.txt', comment='#', 
                   delim_whitespace=True, na_values='...')
deflate = pd.read_csv('./funding_deflators.txt', comment='#', 
                   delim_whitespace=True, na_values='...')
fund=pd.merge(fund,deflate,how='outer',on='Year')
fund['Total_Real']=fund['Total']/fund['Deflator']
fund['NASA_Real']=fund['NASA']/fund['Deflator']
fund['NSF_Real']=fund['NSF']/fund['Deflator']
fund = fund.set_index('Year')

# SETUP PLOTTING PARAMETERS
pdffile = './jobregister_plots.pdf'
pdf = PdfPages(pdffile)
# We have 8 categories for institution class, use colorbrewer2.org,
# 8-class Set1
color8 = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
          '#ff7f00', '#ffff33', '#a65628', '#f781bf']
rainbow = ['#e41a1c', '#ff7f00', '#4daf4a', '#377eb8','#984ea3',]
marker8 = ['o', 's', 'p', '*', '^', '>', 'v', '<']
# STANDARDIZE CATEGORIES, see README.md
# Check out the available categories each year. Note 2008 is the
# "crossover" year.
for yr in set(df.year):
    cats = set(df[df.year == yr]['category'])
    print(yr, len(cats))
    print(cats)

# Combine these as such:
df.category[np.any([df.category == 'TT', df.category ==
                    'Faculty Positions (tenure and tenure-track)'], axis=0)] = 'TT'
df.category[np.any([df.category == 'PostV', df.category == 'Rsrch', df.category ==
                    'Post-doctoral Positions and Fellowships', ], axis=0)] = 'PV'
df.category[np.any([df.category == 'NTT', df.category == 'Visit', df.category ==
                    'Faculty Positions (visiting and non-tenure)'], axis=0)] = 'NTT'
df.category[np.any([df.category == 'MngOth', df.category ==
                    'Other', df.category == 'Science Management'], axis=0)] = 'MO'
df.category[np.any([df.category == 'RsrchSp', df.category == 'Science Engineering',
                    df.category == 'Scientific/Technical Staff', ], axis=0)] = 'RS'
df.category[df.category == 'Pre-doctoral/Graduate Positions'] = 'G'

# CREATE A FEW DATA TABLES
# Print a few tables
# http://stackoverflow.com/questions/34907019/pandas-histogram-by-dates-and-sorted-by-categories

# First table: Job categories by year.
table1 = df.groupby('acyear')['category'].value_counts().unstack(1)
# Add a column with "All"
table1 = pd.concat([table1, pd.DataFrame(
    table1.sum(axis=1), columns=['All'])], axis=1)
table1 = pd.concat([m07t2, table1], axis=0, join='outer')
table1.to_csv('./jobregister_categories_byyear.csv')
# Add degree data to table1, jobs per year, for plotting.
table1 = pd.concat([table1, deg], axis=1, join='outer')

#  First table: Job categories by year, US-only.
#  note that the "Foreign" label is not used consistently!
#  E.g., canadian universities classified as "large academic/small academic"
#  No "foreign" category before 2003
#  Need to scrape country from contact field to get this right.
#  2019: Academic years 2016-2018 now do have this country info.
#  How many are miscategorized?
df['ShouldBeForeign']=(df.country != 'United States of America') & (df.country != 'unknown')
wUS = (df.instclass != 'Foreign') & (df.acyear >= 2003) & (df.ShouldBeForeign == False)
table1US = df[wUS].groupby('acyear')['category'].value_counts().unstack(1)
# Add a column with "All"
table1US = pd.concat([table1US, pd.DataFrame(
    table1US.sum(axis=1), columns=['All'])], axis=1)
#table1US = pd.concat([m07t2, table1US], axis=0, join='outer') # Don't concatenate with pre-2003.
table1US.to_csv('./jobregister_categories_byyear_USonly.csv')
# Add degree data to table1, jobs per year, for plotting.
table1US = pd.concat([table1US, deg], axis=1, join='outer')

# Make a new instclass category, recategorize ones that should be Foreign. 
df['instclass_wforeign']=df['instclass']
df['instclass_wforeign'][df['ShouldBeForeign']]='Foreign'

# Second table: Institution Class by Year
table2 = df.groupby('acyear')['instclass'].value_counts().unstack(
    1).to_csv('./jobregister_instclass_byyear.csv')
table2US = df.groupby('acyear')['instclass_wforeign'].value_counts().unstack(
    1).to_csv('./jobregister_instclass_byyear_USonly.csv')
    

# START PLOTTING. Totally inconsistent methods here.
# PAGE 1A: Plot PhD recipients and funding vs. year. Matches Metcalfe 2008 Figure 1.
plt.cla()
ax = deg.plot(kind='line')
#ax.axvline(2006, color='gray')
ax.set_xlabel('Academic Year')
ax.set_ylabel('U.S. Astronomy PhDs Awarded')
pdf.savefig()

# PAGE 1B: Plot funding vs. year. Other part of Metcalfe 2008 Figure 1.
plt.cla()
ax = fund[['Total_Real','NASA_Real','NSF_Real']].plot(kind='line')
ax.set_xlabel('Fiscal Year')
ax.set_ylabel('Federal Astronomy Research Funding (2009M$)')
pdf.savefig()

# PAGE 1C: Combine the previous two, in a nicer format, for white paper.
plt.cla()
fig,ax1=plt.subplots()
#ax1.plot(deg['AIP'],color=color8[0],linestyle='solid',label='AIP')
ax1.plot(deg['SED'],color=color8[1],linestyle='solid')
ax1.set_xlabel('Academic Year or Fiscal Year')
ax1.set_ylabel('Number of Astronomy PhDs (Solid)')
ax2=ax1.twinx()
ax2.plot(fund['Total_Real'],color='k',linestyle='dashed')
ax2.set_ylabel('Federal Astronomy Research Funds (2009M$, Dashed)',rotation=270,va='bottom')
plt.subplots_adjust(right=0.85)
pdf.savefig()

# PAGE 2: Job Register Ads vs. year. Matches Metcalfe 2008 Figure 3, jobs
# per year
plt.clf()
plt.plot(table1.index, table1['All'], label='All Jobs', color='k')
plt.plot(table1.index, table1['TT'], label='Tenure-Track', color='green')
plt.plot(table1.index, table1[
         'PV'], label='Postdoc/Research', color='b', linestyle='dotted')
plt.plot(table1.index, table1['NTT'],
         label='Non-Tenure-Track', color='r', linestyle='--')
plt.plot(table1.index, table1[
         'RS'], label='Research Support', color='cyan', linestyle='--')
plt.plot(table1.index, table1['MO'], label='Other',
         color='magenta', linestyle='-.')
plt.axvline(2006, color='gray')  # This indicates where Metcalfe 2008 left off.
plt.ylabel('Number of Job Postings on AAS Job Register')
plt.xlabel('Academic Year')
plt.legend(loc='best')
pdf.savefig()

# Metcalfe 2008 Figure 3, job register ads / new PhDs
# Would be best to use UMI measures, but we don't have that.
# Figure out an average ratio between AIP and SED to UMI. Try to use that as an estimate.
# Do not save this plot.
plt.clf()
plt.plot(table1.index, table1['UMI'] / table1['AIP'])
plt.plot(table1.index, table1['UMI'] / table1['SED'])
useavg = np.all([table1.index >= 1990, table1.index <= 2006], axis=0)
avgAIP = np.average(table1['UMI'][useavg] / table1['AIP'][useavg])
avgSED = np.average(table1['UMI'][useavg] / table1['SED'][useavg])
plt.axhline(avgAIP)
plt.axhline(avgSED)
plt.legend(loc='best')
# Do not save this plot.

# PAGE 3: Now plot job register ads/ new PhDs vs. Year, Totals nly
plt.clf()
plt.plot(table1.index, table1['All'] / table1['UMI'],
         label='All Jobs, using UMI', color='k')
plt.plot(table1.index, table1['All'] / (table1['SED'] * avgSED),
         label='All Jobs, using SED to UMI avg')
plt.plot(table1.index, table1['All'] / (table1['AIP'] * avgAIP),
         label='All Jobs, using AIP to UMI avg')
plt.legend(loc='best')
plt.xlabel('Academic Year')
plt.ylabel('Job Register Ads / New U.S. PhD')
pdf.savefig()

# PAGE 4: Job register ads / new PhDs vs. Year, by Category
plt.clf()
plt.plot(table1.index, table1['All'] / (table1['SED'] * avgSED),
         label='All Jobs', color='k')
plt.plot(table1.index, table1['TT'] / (table1['SED'] * avgSED),
         label='Tenure-Track', color='green')
plt.plot(table1.index, table1['PV'] / (table1['SED'] * avgSED),
         label='Postdoc/Research', color='b', linestyle='dotted')
plt.plot(table1.index, table1['NTT'] / (table1['SED'] * avgSED),
         label='Non-Tenure-Track', color='r', linestyle='--')
plt.plot(table1.index, table1['RS'] / (table1['SED'] * avgSED),
         label='Research Support', color='cyan', linestyle='--')
plt.plot(table1.index, table1['MO'] / (table1['SED'] * avgSED),
         label='Other', color='magenta', linestyle='-.')
plt.axvline(2006, color='gray')  # This indicates where Metcalfe 2008 left off.
plt.ylabel('All Job Register Ads / New U.S. PhD')
plt.xlabel('Academic Year')
plt.legend(loc='best')
xlim4=plt.xlim() # Save for next one.
print(xlim4)
ylim4=plt.ylim() # Save for next one.
pdf.savefig()

# PAGE 4b: Job register ads for US positions/ new PhDs vs. Year, by Category
plt.clf()
plt.plot(table1US.index, table1US['All'] / (table1US['SED'] * avgSED),
         label='All Jobs', color='k')
plt.plot(table1US.index, table1US['TT'] / (table1US['SED'] * avgSED),
         label='Tenure-Track', color='green')
plt.plot(table1US.index, table1US['PV'] / (table1US['SED'] * avgSED),
         label='Postdoc/Research', color='b', linestyle='dotted')
plt.plot(table1US.index, table1US['NTT'] / (table1US['SED'] * avgSED),
         label='Non-Tenure-Track', color='r', linestyle='--')
plt.plot(table1US.index, table1US['RS'] / (table1US['SED'] * avgSED),
         label='Research Support', color='cyan', linestyle='--')
plt.plot(table1US.index, table1US['MO'] / (table1US['SED'] * avgSED),
         label='Other', color='magenta', linestyle='-.')
plt.axvline(2006, color='gray')  # This indicates where Metcalfe 2008 left off.
plt.ylabel('US-Only Job Register Ads/ New U.S. PhD')
plt.title('Redone Foreign classification for 2016 and up')
plt.xlabel('Academic Year')
plt.xlim(xlim4) # For visual comparison to the above graph.
plt.ylim(ylim4)
plt.legend(loc='best')
plt.axvline(2016, color='black') # Where new categorization starts
pdf.savefig()


# PLOTS AND STATISTICS OF JUST OUR DATA
# Histogram: Postings by year, broken down by category
# Stacked
ax1 = df.groupby(df.acyear)['category']\
    .value_counts()\
    .unstack(1)\
    .plot(kind='bar', stacked=True, color=color8, figsize=(11, 8))
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10),
           ncol=2, fancybox=True, shadow=True, fontsize=10)
ax1.figure.subplots_adjust(bottom=0.2)
ax1.set_xlabel('Year Posted')
# pdf.savefig(ax1.figure)

# Loop for future plots...
nplot = 7
df.sort_values(['year', 'month'], inplace=True)
for i in range(nplot):
    plt.cla()

    if i == 0:
        group = df.groupby(df.acyear)['category']
        ytitle = ''
        xtitle = 'Academic Year'
    elif i == 1:
        group = df.groupby(df.acyear)['instclass']
        ytitle = 'Original Classification, '
        xtitle = 'Academic Year'
    elif i==2:
        new_df = df[df['year']>2017]
        group=new_df.groupby('year', sort=True)['month']
        ytitle=''
        xtitle = 'Months'
        import pdb; pdb.set_trace()
    elif i == 3:
        group = df.groupby(df.acyear)['instclass_wforeign']
        ytitle = 'Redone Foreign Classification (2016 and up)'
        xtitle = 'Academic Year'
    elif i == 4:
        group = df.groupby(df.category)['instclass_wforeign']
        ytitle = ''
        xtitle = 'Job Category, redone Foreign classification (2016 and up)'
    elif i == 5:
        group = df[df.instclass_wforeign == 'Foreign']
        group = group.groupby(group.year)['category']
        ytitle = 'Foreign Only, '
        xtitle = 'Academic Year'
    elif i == 6:
        group = df[df.instclass_wforeign != 'Foreign']
        group = group.groupby(group.year)['category']
        ytitle = 'US Only, '
        xtitle = 'Academic Year'
    

    # Stacked, then unstacked. No, don't do unstacked.
    for stacked in [True]:  # [True,False]
        plt.cla()
        if i == 2:
            #Loop over groups to enable each year to have a different marker for colorblind readability
            for igroup, imarker, icolor in zip(group, marker8, rainbow):
                ax = igroup[1].value_counts(sort=False).plot(kind='line', color=icolor, ax=ax1,figsize=(11, 8), 
                                            marker=imarker, markersize=8, label=igroup[0])
            ax.set_xticks(np.arange(1,13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            ax.grid(axis='x', alpha=0.2)

        else:
            ax = group.value_counts().unstack(1).plot(kind='bar',
                                                  color=color8, ax=ax1,
                                                  stacked=stacked, figsize=(11, 8))
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10),
                  ncol=3, fancybox=True, shadow=True, fontsize=10)
        ax.set_ylabel(ytitle + 'Number of Job Register Ads')
        ax.set_xlabel(xtitle)
        if i>=4: ax.axvline(2015.5,color='gray')
        pdf.savefig(ax.figure)
        
    # Then stacked and percentage.
    plt.cla()
    ax = group.value_counts(normalize=True).unstack(1).plot(kind='bar', color=color8, ax=ax1,
                                                            stacked=True, figsize=(11, 8))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
              ncol=3, fancybox=True, shadow=True, fontsize=10)
    ax.set_ylabel(ytitle + 'Fraction of Job Register Ads')
    ax.set_xlabel(xtitle)
    pdf.savefig(ax.figure)

    # Line plot of percentage. No, don't do.
    # plt.cla()
    # ax=group.value_counts(normalize=True).unstack(1).plot(kind='line',ax=ax1,color=color8,
    #        stacked=False,figsize=(11,8))
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
    #          ncol=3, fancybox=True, shadow=True,fontsize=10)
    # ax.set_ylabel(ytitle)
    # pdf.savefig(ax.figure)

# Histograms, one subplot per job type, with histogram of institutions
plt.cla()
ax = df.groupby(df.instclass)['category']\
    .value_counts().unstack(1).plot(kind='bar', color=color8, subplots=True, ax=ax1,
                                    layout=(2, 4), legend=False, figsize=(11, 8), sharex=True)
pdf.savefig(ax[0][0].figure)

# Histograms, one subplot per job type, with histogram of institutions
plt.cla()
ax = df.groupby(df.instclass_wforeign)['category']\
    .value_counts().unstack(1).plot(kind='bar', color=color8, subplots=True, ax=ax1,
                                    layout=(2, 4), legend=False, figsize=(11, 8), sharex=True)
pdf.savefig(ax[0][0].figure)

# close PDF
pdf.close()

# Months
df.groupby('month')['month'].value_counts()
for mo in np.arange(12) + 1:
    print(mo, np.sum(df.month == mo) / float(len(df)))
