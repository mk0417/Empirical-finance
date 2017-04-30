'''----------------------------------------------------------------------------------------------------
Basic statistics

Last tutorial, we import data and have done some data cleaning work. This tutorial will use the clean
data to compute summary statistics of variables and to present cross sectional statistics by date.
----------------------------------------------------------------------------------------------------'''

# Import required libraries
import pandas as pd

pd.set_option('display.width', 180)

# Read data
data_path = '/users/ml/git/'
crsp_monthly = pd.read_csv(data_path + 'crsp_monthly_clean.txt', sep='\t', engine='python')

# Check data type of each variable
'''---------------------------------------------------------------------------------------------------
If there is mixed type of data in a column (e.g. both numeric and string variable in a column),
Python will read it as object. We need to clarify the data type of the variable.

For example, return should be numeric otherwise we cannot do any calculation in Python. However,
CRSP return data contains missing codes, i.e. some letters (e.g. 'A', 'B' and 'S') rather than numeric
value to indicate the reason why the return is missing. Therefore, we need to convert these missing
codes to missing value in numeric format which is NaN.

Another example is date format, the date in the data is not date format after you import the data.
This could make problems when you want to compute the difference between dates (e.g. 20100101 should
be one day after 20091231, but if you do not convert them into date format, it will return
20100101-20091231=8870).
---------------------------------------------------------------------------------------------------'''
print crsp_monthly.dtypes

# Convert return to numeric variable otherwise we cannot use return to do any calculation
for i in ['ret', 'siccd', 'dlret']:
    crsp_monthly[i] = pd.to_numeric(crsp_monthly[i], errors='coerce')

# Convert date to date format
crsp_monthly['date'] = pd.to_datetime(crsp_monthly['date'], format='%Y%m%d')
crsp_monthly['yr_mo'] = crsp_monthly['date'].apply(lambda x: x.year) * 100 + crsp_monthly['date'].apply(lambda x: x.month)

# Output data
'''
Now we have the final dataset after sample selection (in previous tutorial) and data type adjustment
'''
crsp_monthly.to_csv(data_path+'crsp_monthly_clean_1.txt', sep='\t', index=False)

# Compute summary statistics
'''Pooled statistics'''
stats = crsp_monthly[['ret', 'vol', 'bid', 'ask']].describe().T
for i in stats.columns:
    stats[i] = stats[i].apply(lambda x: format(x, '.3f'))

print stats

'''
Cross section statistics
1. For each month, we compute summary statistics across stocks.
2. Then we compute the time-series average of cross sectional statistics.
'''
'''First, we will take return as example'''
stats_cs_ret = crsp_monthly.groupby('yr_mo')['ret'].describe()
stats_cs_ret = stats_cs_ret.unstack()

print 'number of month %s' % len(stats_cs_ret)

stats_cs_ret = pd.DataFrame({'ret': stats_cs_ret.mean()}).T
print stats_cs_ret

'''Add more variables to present results'''
stats_cs = pd.DataFrame()
for i in ['ret', 'vol', 'bid', 'ask']:
    summary = crsp_monthly.groupby('yr_mo')[i].describe()
    summary = pd.DataFrame({i: summary.unstack().mean()}).T
    stats_cs = pd.concat([stats_cs, summary])

for i in stats_cs.columns:
    stats_cs[i] = stats_cs[i].apply(lambda x: format(x, '.3f'))

print stats_cs
