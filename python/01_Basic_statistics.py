import pandas as pd

pd.set_option('display.width', 180)

data_path = '/users/ml/git/'
crsp_monthly = pd.read_csv(data_path + 'crsp_monthly_clean.txt', sep='\t', engine='python')

# Check data type of each variable.
print crsp_monthly.dtypes

# Convert return to numeric variable otherwise we cannot use return to do any calculation
for i in ['ret', 'siccd', 'dlret']:
    crsp_monthly[i] = pd.to_numeric(crsp_monthly[i], errors='coerce')

# Convert date to date format
crsp_monthly['date'] = pd.to_datetime(crsp_monthly['date'], format='%Y%m%d')
crsp_monthly['yr_mo'] = crsp_monthly['date'].apply(
    lambda x: x.year) * 100 + crsp_monthly['date'].apply(lambda x: x.month)

# Compute summary statistics
'''Pooled statistics'''
stats = crsp_monthly[['ret', 'vol', 'vwretd']].describe().T
for i in stats.columns:
    stats[i] = stats[i].apply(lambda x: format(x, '.3f'))

print stats

'''Cross section statistics'''
stats_cs_ret = crsp_monthly.groupby('yr_mo')['ret'].describe()
stats_cs_ret = stats_cs_ret.unstack()
print stats_cs_ret

print 'number of month %s' % len(stats_cs_ret)
print stats_cs_ret.mean()
