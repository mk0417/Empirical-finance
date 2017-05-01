'''------------------------------------------------------------------------------------------------
   Beta

   Beta is the most important concept in modern finance. It measures market risk or systematic
   risk. Specifically, it uncovers how individual stock return correlates market performance. In
   a rational market, stock return should be determined by beta, i.e. stock return is the
   compensation for taking market risk.
------------------------------------------------------------------------------------------------'''

import pandas as pd
import statsmodels.api as sm
from matplotlib import pyplot as plt
import seaborn as sns

pd.set_option('display.width', 180)

data_path = '/users/ml/git/'

# Read clean data
'''
The speed of reading data should be faster than before because there is no mixed type for each
variable. Therefore, computer does not need to allocate resource to guess the type of data.
'''
crsp_monthly = pd.read_csv(data_path+'crsp_monthly_clean_1.txt', sep='\t')
permno_list = crsp_monthly.drop_duplicates(subset='permno')['permno']
print len(permno_list)

stock_ret = crsp_monthly[(crsp_monthly['ret'].notnull()) & (crsp_monthly['vwretd'].notnull())][['permno','date','ret','vwretd']]
permno_list = stock_ret.drop_duplicates(subset='permno')['permno']
print len(permno_list)

# Use at least 36-month historical information to estimate beta
permno_num = pd.DataFrame({'n': stock_ret.groupby('permno')['ret'].count()})
permno_num = permno_num[permno_num['n']>=36]
print len(permno_num)

# Define OLS regression
def ols_reg(y,x):
    est = sm.OLS(y,sm.add_constant(x)).fit()
    return est

# Run OLS regression to estimate beta for each stock
beta = []
for i in permno_num.index:
    ret_data = stock_ret[stock_ret['permno']==i]
    est = ols_reg(ret_data['ret'],ret_data['vwretd'])
    beta.append((i,est.params[1]))

beta_1 = pd.DataFrame(beta, columns=['permno','beta'])
print beta_1['beta'].describe()

# Plot the distribution of beta
_,ax_beta = plt.subplots(1,1,figsize=(8,3))
beta_1['beta'].hist(bins=100, ax=ax_beta)
plt.show()

# Rolling beta
'''
Rolling beta can show the persistence of beta
'''
stock_ret_1 = stock_ret.pivot(index='date',columns='permno',values='ret')
stock_ret_1.columns = [str(i) for i in stock_ret_1.columns]
mktret = pd.DataFrame(stock_ret.drop_duplicates(subset='date')[['date','vwretd']])
mktret = mktret.sort_values('date')
mktret.index = mktret['date']
del mktret['date']
stock_ret_1 = stock_ret_1.join(mktret)
print len(stock_ret_1)

beta_rolling = []
window = 60 # rolling window: number of observation to estimate beta
''' Just try first 10 stocks '''
for i in stock_ret_1.columns[:10]:
    ret_data = stock_ret_1[[i,'vwretd']]
    ret_data = ret_data[(ret_data[i].notnull()) & (ret_data['vwretd'].notnull())]
    ret_data.sort_index(inplace=True)
    if len(ret_data) >= window:
        for j in range(len(ret_data)-window):
            est = ols_reg(ret_data.ix[ret_data.index[j:j+window-1],i],ret_data.ix[ret_data.index[j:j+window-1],'vwretd'])
            beta_rolling.append((i,ret_data.index[j+window-1],est.params[1]))

beta_rolling_1 = pd.DataFrame(beta_rolling,columns=['permno','date','beta'])

# Plot rolling beta
beta_stock_list = beta_rolling_1.drop_duplicates(subset='permno')['permno'].reset_index(drop=True)
print len(beta_stock_list)

plt.close('all')
_,axes = plt.subplots(2,3,figsize=(15,6))
for i,j in zip(axes.flatten(),beta_stock_list):
    pd.DataFrame(beta_rolling_1[beta_rolling_1['permno']==j]['beta']).reset_index(drop=True).plot(ax=i)
    i.legend([])

plt.show()
