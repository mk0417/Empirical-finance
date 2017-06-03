import pandas as pd

pd.set_option('display.width', 180)

crsp_file = '/users/ml/git/crsp_monthly_clean_1.txt'

crspm = pd.read_csv(crsp_file, sep='\t', low_memory=False)
crspm = crspm[['permno','date','ret']]
crspm = crspm.sort_values(['permno','date']).reset_index(drop=True)
crspm['ret_lag1'] = crspm.groupby('permno')['ret'].shift(1)

# Function: mean and standard deviation of past n-month return for each month
def rolling_past(n):
    """
    The past n-month for month t is from month t-1 to t-n, so it does not include month t.
    """
    rolling_mean = lambda x: pd.Series.rolling(x, window=n, min_periods=n-1).mean()
    rolling_std = lambda x: pd.Series.rolling(x, window=n, min_periods=n-1).std()
    crspm['pre'+str(n)+'mean'] = crspm.groupby('permno')['ret_lag1'].apply(rolling_mean)
    crspm['pre'+str(n)+'std'] = crspm.groupby('permno')['ret_lag1'].apply(rolling_std)

# Average and std of past 6-, 9- and 12-month return in each month
for i in [6,9,12]:
    rolling_past(i)

crspm = crspm.sort_values(['permno','date'],ascending=[True,False]).reset_index(drop=True)

# Function: mean and standard deviation of post n-month return for each month
def rolling_post(n):
    """
    The post n-month for month t is from month t to t+n-1, so it includes month t.
    """
    rolling_mean = lambda x: pd.Series.rolling(x, window=n, min_periods=n-1).mean()
    rolling_std = lambda x: pd.Series.rolling(x, window=n, min_periods=n-1).std()
    crspm['post'+str(n)+'mean'] = crspm.groupby('permno')['ret'].apply(rolling_mean)
    crspm['post'+str(n)+'std'] = crspm.groupby('permno')['ret'].apply(rolling_std)

# Average and std of post 6-, 9- and 12-month return in each month
for i in [6,9,12]:
    rolling_post(i)

crspm = crspm.sort_values(['permno','date']).reset_index(drop=True)
