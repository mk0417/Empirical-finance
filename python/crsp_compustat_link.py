import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pandasql import sqldf

pysql = lambda sql: sqldf(sql,globals())
pd.options.display.width = 180


# --------------------------------------- Merge CRSP and Compustat without CRSP-Compustat Merge table -------------------------------------

# PERMNO list from CRSP monthly stock file
# CRSP monthly file: this file (msf.h5) already deletes duplicates 
msf = pd.read_hdf('/users/ml/data/clean/wrds/msf.h5', 'msf', columns=['permno','permco','cusip','date','ncusip','comnam','ticker','shrcd','exchcd'])
msf_1 = msf.copy()
msf_1['yrm'] = (msf_1['date']/100).astype('int')
msf_permno = msf_1.drop_duplicates(subset='permno')[['permno','cusip','ncusip']]
msf_permno.columns = ['permno','msf_cusip','msf_ncusip']

# --------------------------------------------------------- Read CUSIP list -----------------------------------------------------------
# CRSP CUSIP list
stocknames = pd.read_csv('~/data/wrds/raw/stocknames.txt',sep='\t')
stocknames.columns = stocknames.columns.map(str.lower)
stocknames = stocknames.merge(msf_permno,how='inner',on='permno')
# Compustat CUSIP list
security = pd.read_csv('~/data/wrds/raw/security.txt',sep='\t')
security.columns = security.columns.map(str.lower)
security['cusip'] = security['cusip'].apply(lambda x: str(x)[:8])
security_1 = security[(security['cusip'].notnull())&(security['cusip']!='nan')&(security['excntry']=='USA')].copy()
comp_cusip = security_1.drop_duplicates(subset='cusip')[['gvkey','cusip']].sort_values('gvkey').reset_index(drop=True)


# ------------------------------------------ PERMNO-GVKEY link using CUSIP ----------------------------------------------
stocknames_1 = stocknames[stocknames['cusip'].notnull()].copy()
crsp_cusip = stocknames_1.drop_duplicates(subset='cusip')[['permno','cusip']].sort_values('permno').reset_index(drop=True)
cusip_comp_link = crsp_cusip.merge(comp_cusip,how='inner',on='cusip')



# ---------------------------------------------- PERMNO-GVKEY using NCUSIP ------------------------------------------
stocknames_2 = stocknames[stocknames['ncusip'].notnull()].copy()
crsp_ncusip = stocknames_2.drop_duplicates(subset='ncusip')[['permno','ncusip']].sort_values('permno').reset_index(drop=True)
crsp_ncusip['cusip'] = crsp_ncusip['ncusip']
del crsp_ncusip['ncusip']
# Here the CUSIP is NCUSIP, so one PERMNO-GVKEY pair may have multiple CUSIPs
ncusip_comp_link = crsp_ncusip.merge(comp_cusip,how='inner',on='cusip')
#-------------------------------------- here demonstrate why duplicates appear
ncusip_comp_link_dup = ncusip_comp_link[ncusip_comp_link.duplicated(['permno','gvkey'],keep=False)]
stocknames[stocknames['permno']==10801]
security_1[security_1['gvkey']==12699]
#---------------------------------------

# Remove duplicated PERMNO-GVKEY pair
ncusip_comp_link = ncusip_comp_link.drop_duplicates(subset=['permno','gvkey']).sort_values('permno').reset_index(drop=True)


# --------------------------------------------- PERMNO-GVKEY link using CUSIP and NCUSIP ------------------------------------------------
# You will miss some PERMNO-GVKEY pair if you use CUSIP only or NCUSIP only
# So, the strategy is to use both CUSIP and NCUSIP to maximize the matched PERMNO-GVKEY pair
# And I will show what you will miss later if you either use CUSIP only or NCUSIP only
ncusip_cusip_combine = ncusip_comp_link[['permno','gvkey']].merge(cusip_comp_link[['permno','gvkey']],how='outer',on='permno')
ncusip_cusip_combine.columns = ['permno','gvkey_nc','gvkey_cc']
ncusip_cusip_combine_1 = ncusip_cusip_combine.copy()
# If there is missing PERMNO-GVKEY pair by NCUSIP, then use PERMNO-GVKEY pair based on CUSIP
ncusip_cusip_combine_1['gvkey_nc'] = np.where(ncusip_cusip_combine_1['gvkey_nc'].isnull(),ncusip_cusip_combine_1['gvkey_cc'],ncusip_cusip_combine_1['gvkey_nc'])
del ncusip_cusip_combine_1['gvkey_cc']
ncusip_cusip_combine_1.columns = ['permno','gvkey']


# ---------------------------------------- Check missing if use CUSIP only or NCUSIP only --------------------------------------------
ncusip_cusip_same = ncusip_cusip_combine[ncusip_cusip_combine['gvkey_nc']==ncusip_cusip_combine['gvkey_cc']].copy()
len(ncusip_cusip_same)
ncusip_cusip_diff = ncusip_cusip_combine[(ncusip_cusip_combine['gvkey_nc']!=ncusip_cusip_combine['gvkey_cc'])].copy()
len(ncusip_cusip_diff)
ncusip_cusip_diff_gvkey = ncusip_cusip_diff[(ncusip_cusip_diff['gvkey_nc'].notnull())&(ncusip_cusip_diff['gvkey_cc'].notnull())].copy()
len(ncusip_cusip_diff_gvkey)
ncusip_cusip_no_nc = ncusip_cusip_diff[ncusip_cusip_diff['gvkey_nc'].isnull()].copy()
len(ncusip_cusip_no_nc)
ncusip_cusip_no_cc = ncusip_cusip_diff[ncusip_cusip_diff['gvkey_cc'].isnull()].copy()
len(ncusip_cusip_no_cc)

# If you merge by CUSIP only then you will miss PERMNO-GVKEY pair in two scenarios:
# After a corporate event, especially merge and aquisition, a company may chnages its name. However CRSP and Compustat have different treatments in some cases.
# 1. CRSP may consider they are the same firm but Compustat may consider they are different firms
# 2. Compustat does not have information about the firm after the event, so the CUSIP in Compustat is the CUSIP at the event time. But CRSP may contain
#    the information abou the firm and update CUSIP to the lastest one. For such firm, you can only use NCUSIP in CRSP to match.

# Example of scenario 1
ncusip_cusip_diff_gvkey.head()

stocknames[stocknames['permno']==10051]

security_1[security_1['gvkey']==13445][['tic','gvkey','iid','cusip','exchg','excntry','isin','tpci']]

security_1[security_1['gvkey']==16456][['tic','gvkey','iid','cusip','exchg','excntry','isin','tpci']]

# Example of scenario 2
ncusip_cusip_no_cc.head()

stocknames[stocknames['permno']==10066]

security_1[security_1['gvkey']==1008][['tic','gvkey','iid','cusip','exchg','excntry','isin','tpci']]

# If you merge by NCUSIP only then you will miss PERMNO-GVKEY pair in the following scenarios:
# Sometimes, there is no valid NCUSIP for a stock in CRSP, so you can only rely on CUSIP to match such stock
ncusip_cusip_no_nc.head()

stocknames_1[stocknames_1['permno']==10532]

security_1[security_1['gvkey']==1764][['tic','gvkey','iid','cusip','exchg','excntry','isin','tpci']]



# ----------------------------  Generate PERMNO-GVKEY link table Using NCUSIP+CUSIP and name range -----------------------------
num_ncusip = stocknames.groupby('permno')['ncusip'].count().to_frame('n')
num_ncusip['permno'] = num_ncusip.index
no_ncusip = num_ncusip[num_ncusip['n']==0].sort_values('permno').reset_index(drop=True)
crsp_names = stocknames.copy()
crsp_names = crsp_names.merge(no_ncusip,how='left',on='permno')
crsp_names['ncusip'] = np.where(crsp_names['n']==0,crsp_names['cusip'],crsp_names['ncusip'])

comp_names = security_1.copy()
comp_names['ncusip'] = comp_names['cusip']
del comp_names['cusip']
crsp_comp_names = crsp_names[['permno','cusip','ncusip','comnam','namedt','nameenddt']].merge(comp_names[['gvkey','ncusip']],how='left',on='ncusip')
crsp_comp_names = crsp_comp_names.sort_values(['permno','namedt']).reset_index(drop=True)
crsp_comp_names['gvkey'] = crsp_comp_names.groupby('permno')['gvkey'].bfill()
crsp_comp_names = crsp_comp_names[crsp_comp_names['gvkey'].notnull()]

permno_gvkey = pysql("""select a.permno,a.cusip,a.ncusip,a.comnam,a.ticker,b.namedt,b.nameenddt,b.gvkey
                        from msf_1 a inner join crsp_comp_names b
                        on a.permno=b.permno and a.date>=b.namedt and a.date<=b.nameenddt;""")

permno_gvkey = permno_gvkey.drop_duplicates(subset=['permno','gvkey','namedt'])
permno_gvkey = permno_gvkey.sort_values(['permno','namedt']).reset_index(drop=True)

# Save PERMNO-GVKEY link table
permno_gvkey.to_csv('~/data/clean/wrds/permno_gvkey_link.txt',sep='\t',index=False)

# Check the percent of match over time ----------------------------------------
msf_2 = msf_1[(msf_1['shrcd'].isin([10,11]))&(msf_1['exchcd'].isin([1,2,3]))].copy()
link_ts_all = msf_2.groupby('yrm')['permno'].count().to_frame('num').sort_index()
link_ts = pysql("""select a.*
                   from msf_2 a inner join permno_gvkey b
                   on a.permno=b.permno and a.date>=b.namedt and a.date<=b.nameenddt;""")

link_ts_1 = link_ts.groupby('yrm')['permno'].count().to_frame('matched num').sort_index()
link_percent = link_ts_1.join(link_ts_all).sort_index()
link_percent = link_percent[link_percent.index>=196307]
link_percent['percent of matched stock'] = link_percent['matched num'] / link_percent['num']
link_percent.index = pd.to_datetime(link_percent.index,format='%Y%m')
link_percent.index.name = 'date'
plt.close('all')
fig1,(ax1,ax2) = plt.subplots(2,1,figsize=(10,6),sharex=True)
link_percent[['num','matched num']].plot(ax=ax1)
ax1.set_title('Number of stocks from 1963 to 2016')
link_percent['percent of matched stock'].plot(ax=ax2)
ax2.set_title('Percent of matched stock from 1963 to 2016')
ax2.axhline(0.8,color='r',linewidth=1)
plt.show()
