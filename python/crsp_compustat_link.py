import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pandasql import sqldf

pysql = lambda q: sqldf(q,globals())
pd.options.display.width = 180


# ---------------------------------------------------------- Merge CRSP and Compustat without CRSP-Compustat Merge table -------------------------------------------------------


# --------------------------------------------------------- Read required data -----------------------------------------------------------
# Read CRSP stock history file
msenames = pd.read_csv('/users/ml/data/wrds/raw/msenames.txt',sep='\t')
msenames.columns = msenames.columns.map(str.lower)
msenames_1 = msenames[['permno','cusip','ncusip','namedt','nameendt','comnam','ticker','shrcd','exchcd']].copy()
msenames_1 = msenames_1.sort_values(['permno','namedt']).reset_index(drop=True)

# Read Compustat stock history file
security = pd.read_csv('/users/ml/data/wrds/raw/security.txt',sep='\t')
security.columns = security.columns.map(str.lower)
# Convert Compustat 9-digit CUSIP to 8-digit CUSIP
security['cusip'] = security['cusip'].apply(lambda x: str(x)[:8])
security['ncusip'] = security['cusip']
# Remove missing CUSIP and keep stocks listing in US stock exchanges (this can remove dual listing in US and Canada)
security_1 = security[(security['cusip'].notnull())&(security['cusip']!='nan')&(security['excntry']=='USA')].copy()
security_1 = security_1.sort_values('gvkey').reset_index(drop=True)

# Read CRSP monthly file
# This file already deletes duplicates and keeps only stocks listing in NYSE/NASDAQ/AMEX
msf = pd.read_hdf('/users/ml/data/clean/wrds/msf.h5', 'msf', columns=['permno','permco','cusip','date','ncusip','comnam','ticker','shrcd','exchcd'])
# Keep common shares and stock with NCUSIP
# Stocks without NCUSIP in their whole life cannot match with Compustat, because such stocks have no official CUSIP and the CUSIP is a dummy CUSIP assigned by CRSP
msf_1 = msf[msf['shrcd'].isin([10,11])&(msf['ncusip'].notnull())].copy()


# -----------------------------------------------------------------------------------------------------------------------------------------
# ----------------- Here is the demonstration why we tick out stocks without NCUSIP over their entire periods -----------------------------
# List of stocks with NCUSIP
with_ncusip = msf_1.drop_duplicates(subset='permno')[['permno','ncusip','cusip']].copy()
print('Number of unique stocks with NCUSIP: {}'.format(len(with_ncusip)))
# List of stocks without NCUSIP
no_ncusip = msf[(msf['shrcd'].isin([10,11]))&(msf['ncusip'].isnull())].copy()
no_ncusip = no_ncusip.drop_duplicates(subset='permno')[['permno','ncusip','cusip']]
print('Number of unique stocks without NCUSIP: {}'.format(len(no_ncusip)))
# Generate list of stocks without NCUSIP for the entire period
# Some stocks may have NCUSIP in the later period but do not have NCUSIP in the eariler period, so if we merge with_cusip and no_cusip, then we will get non-missing CUSIP from with_cusip
# If we get missing CUSIP from with_cusip, then it means that the stock never have NCUSIP
no_ncusip_1 = with_ncusip.merge(no_ncusip[['permno']],how='outer',on='permno')
no_ncusip_1 = no_ncusip_1[no_ncusip_1['cusip'].isnull()]
print('Number of unique stocks without NCUSIP for their whole life: {}'.format(len(no_ncusip_1)))
# Merge with Compustat stocks and we should match nothing
no_ncusip_match = no_ncusip_1.merge(security_1,how='inner',on='cusip')
print('Number of match if stocks without NCUSIP: {}'.format(len(no_ncusip_match)))
# ------------------------------------------------------------------------------------------------------------------------------------------



# ------------------------------------------ PERMNO-GVKEY link using current CUSIP ----------------------------------------------
# The drawback of this way is that the merge is not accurate if you do not download the two databases at the same time.
# For example, your CRSP is downloaded 2 years ago and your Compustat is downloaded recently. Some CUSIPs may already change and be updated then you can never match them by CUSIP.
crsp_cusip = msf_1.drop_duplicates(subset='cusip')[['permno','cusip','ncusip','comnam','ticker']]
crsp_cusip = crsp_cusip.sort_values('cusip').reset_index(drop=True)
link_cc_all = crsp_cusip.merge(security_1[['gvkey','cusip']],how='left',on='cusip')
link_cc = crsp_cusip.merge(security_1[['gvkey','cusip']],how='inner',on='cusip')
print('Number of matched PERMNO-GVKEY: {}'.format(len(link_cc)))
print('Percent of match: {:3.1%}'.format(len(link_cc)/len(link_cc_all)))


# ------------------------------------- PERMNO-GVKEY link using NCUSIP and date range -------------------------------------------
# Keep stocks with NCUSIP respect to correct date range
# Observations may exist even after the end of name
ncusip_track = pysql("""select a.permno,a.cusip,a.ncusip,a.date,a.comnam,a.ticker,b.namedt,b.nameendt
                   from msf_1 a inner join msenames_1 b on a.permno=b.permno and a.date>=b.namedt and a.date<=b.nameendt;""")

permno_gvkey = msenames_1.merge(security_1[['gvkey','ncusip']],how='inner',on='ncusip')
permno_gvkey = permno_gvkey.sort_values(['permno','ncusip']).reset_index(drop=True)
link_nc_all = ncusip_track[['permno','cusip','ncusip']].merge(permno_gvkey[['permno','gvkey']],how='left',on='permno')
link_nc_all = link_nc_all.drop_duplicates(subset='permno')
link_nc = ncusip_track[['permno','cusip','ncusip']].merge(permno_gvkey[['permno','gvkey']],how='inner',on='permno')
link_nc = link_nc.drop_duplicates(subset=['permno','gvkey'])
link_nc = link_nc.sort_values(['permno','gvkey']).reset_index(drop=True)
print('Number of matched PERMNO-GVKEY: {}'.format(len(link_nc)))
print('Percent of match: {:3.1%}'.format(len(link_nc)/len(link_nc_all)))
