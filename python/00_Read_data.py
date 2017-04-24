# Import required libraries
import pandas as pd

# Read CRSP monthly data
'''Data is downloaded from WRDS between 1980 to 2016'''
'''data file name is crsp_monthly.txt'''
data_path = '/users/ml/git/'    # change to your data folder
crsp_monthly_raw = pd.read_csv(data_path + 'crsp_monthly.txt', sep='\t', engine='python')
print 'number of observations from raw CRSP data: %s' % len(crsp_monthly_raw)
crsp = crsp_monthly_raw.copy()

# Keep stocks in NYSE, AMEX and NASDAQ
exchanges = (crsp['exchcd'] == 1) | (crsp['exchcd'] == 2) | (crsp['exchcd'] == 3)
crsp = crsp[exchanges]
print 'number of observations (NYSE, AMEX, NASDAQ): %s' % len(crsp)

# Keep common stocks
share_types = (crsp['shrcd'] == 10) | (crsp['shrcd'] == 11)
crsp = crsp[share_types]
print 'number of observations (common stocks): %s' % len(crsp)

# Remove duplicates
crsp = crsp.drop_duplicates(subset=['permno', 'date'], keep='last')
print 'number of observations (delete duplicates): %s' % len(crsp)

# Sort data
crsp = crsp.sort_values(['permno', 'date']).reset_index(drop=True)
print crsp.head(10)

# Save clean data for future use
crsp.to_csv(data_path + 'crsp_monthly_clean.txt', sep='\t', index=False)
