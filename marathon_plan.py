'''
A program to show the weekly mileage for a full marathon training program.

First created: 2018-06-12.
Last modification: 2020-08-02.
Created by Angelo Varlotta (2018).
'''

from pandas import Series, DataFrame, read_csv
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from sys import argv
from math import ceil
import re
import os

# use classic style
plt.style.use('barplot-style.mplstyle')

# file and title names
fname = os.path.abspath(argv[1])
base_file = os.path.basename(fname)
root_file, file_ext = os.path.splitext(base_file)
title, ext_num = re.split('_', root_file)
title_name = title.title()+' '+str(ext_num)

# distances
dists = read_csv(fname, header=0)

# weekly cumulative distances
cumul_kms = Series({x: dists.T[x].sum() for x in dists.T.columns})


# truncate color map
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


cmap = plt.get_cmap('jet')
new_cmap = truncate_colormap(cmap, 0.3, 0.8)

# stacked bar plot
ax = dists.plot(kind='bar', stacked=True, cmap=new_cmap,
                fontsize=13, width=0.75)

# annotate cumulative mileage for each week
for lb, x, y in zip(cumul_kms.values, cumul_kms.index, cumul_kms.values):
    plt.annotate('{0:.1f}'.format(lb), xy=(x, y), ha='center',
                 va='bottom', size=12, weight='bold', color='k')

# weekly individual mileage for each day of week
cum_week_dists = DataFrame(
    {wk_num: dists.loc[wk_num].cumsum() for wk_num in dists.index})

# annotate individual mileage for each day of week
for x in dists.index:
    for lb, y in zip(dists.loc[x], cum_week_dists.T.loc[x]):
        if lb != 0.0:
            plt.annotate('{0:.1f}'.format(lb), xy=(x, y-1.5), ha='center',
                         va='top', size=12, color='k')

# plot legend
ax.legend(fontsize=11, loc=0)

# 5% plot padding in each direction
# ax.margins(0.05)

# x-axis label and tick labels
ax.set_xlabel('Week number')
ax.set_xticklabels(dists.index+1, rotation=0)

# y-axis tick frequency and label
ax.set_yticks(range(ceil(cumul_kms.max())), minor=True)
ax.set_ylabel('Weekly total distance (km)')

# plot title
ax.set_title('Weekly progression for '+str(title_name) +
             ' marathon training program')

# grid style: dotted
# ax.grid(linestyle=':')
# plt.tight_layout()
plt.savefig('stacked2.png')
# plt.show()
