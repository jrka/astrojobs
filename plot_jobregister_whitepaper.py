import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


df = pd.read_csv('./jobregister_whitepaper_plot.csv')

# Colorbrewer 3-class Dark2
color3=['#1b9e77','#d95f02','#7570b3']
width=0.3

plt.cla()
fig,ax = plt.subplots()
ax.set_xlabel('Academic Year')
ax.set_ylabel('Number of Job Postings (Bar Plots)')

# Create stacked bar plots for each category, so just shift them 
# slightly so they are also side by side per year.

ax.bar(np.array(df['acyear'])-width,np.array(df['US PV']),
    color=color3[0],edgecolor='black',width=width,label='Postdoctoral')
ax.bar(np.array(df['acyear'])-width,np.array(df['Foreign PV']),
    bottom=np.array(df['US PV']),color=color3[0],hatch='///',
    edgecolor='black',width=width)

ax.bar(np.array(df['acyear']),np.array(df['US RS + TT + MO']),
    color=color3[1],edgecolor='black',width=width,label='TT Faculty, Science Management/Staff, Other')
ax.bar(np.array(df['acyear']),np.array(df['Foreign RS + TT + MO']),
    bottom=np.array(df['US RS + TT + MO']),color=color3[1],hatch='///',
    edgecolor='black',width=width)

ax.bar(np.array(df['acyear'])+width,np.array(df['US NTT']),
    color=color3[2],edgecolor='black',width=width,label='Non-TT and Visiting Faculty')
ax.bar(np.array(df['acyear'])+width,np.array(df['Foreign NTT']),
    bottom=np.array(df['US NTT']),color=color3[2],hatch='///',
    edgecolor='black',width=width)

ax.legend(loc='best')

ax2=ax.twinx()
deg = pd.read_csv('./degrees.txt', comment='#',
                  delim_whitespace=True, na_values='...')
ax2.plot(deg['Year'],deg['SED'],color='k')
ax2.set_xlim(2002,2019)
ax2.set_ylabel('Number of Astronomy PhDs (Black Line)',va='bottom',rotation=270)
ax2.set_ylim(ax.set_ylim())
plt.subplots_adjust(right=0.85)

plt.savefig('jobregister_whitepaper_plot.png')