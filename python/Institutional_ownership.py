'''------------------------------------------------------------------------------------------------
    Institutional ownership
    This tutorial is to demonstrate how to calculate institutional ownership using Thomson Reuters
    13F database.
    Institutional ownership is an important variable in many finance fields. For example, it is
    a proxy of limits-to-arbitage, i.e. higher institutional ownership suggests low
    limits-to-arbitage; high institutional ownership indicates higher level of market efficiency
    because institutional investors are much more rational than individual investors; company
    disclosure is positively correlated with institutional ownership; the increase of institutional
    ownership can reduce information asymmetry between managers and outside investors or agency
    problem.
------------------------------------------------------------------------------------------------'''


import pandas as pd

pd.set_option('display.width', 180)

tr13f_path = '/users/ml/data/wrds/raw/' # change to your folder
crsp_path = '/users/ml/data/clean/' # change to your folder

# Read institutional ownership data
'''Chunk by chunk can boost the speed of reading large dataset'''
def chunk_read(filename):
    chunk_data = pd.read_csv(tr13f_path+filename+'.txt', sep='\t', iterator=True, chunksize=10**5, low_memory=False, dtype={'cusip': str})
    return pd.concat(chunk_data, ignore_index=True)

chunk_1 = chunk_read('inst13f_1980_1989')
chunk_2 = chunk_read('inst13f_1990_1999')
chunk_3 = chunk_read('inst13f_2000_2008')
chunk_4 = chunk_read('inst13f_2009_2015')

tr13f = pd.concat([chunk_1,chunk_2,chunk_3,chunk_4], ignore_index=True)
print 'total observations: %s' %len(tr13f)

# Keep shares greater than 0 and delete missing CUSIP
tr13f_1 = tr13f[['cusip','rdate','mgrno','fdate','shares']].copy()
tr13f_1 = tr13f_1[(tr13f_1['cusip'].notnull())&(tr13f_1['shares']>0)].reset_index(drop=True)

# Remove duplicates
'''TR-13F has multiple FDATEs for a given CUSIP-RDATE-MGRNO and we only keep the first observation in such case'''
tr13f_2 = tr13f_1.sort_values(['cusip','rdate','mgrno','fdate'])
tr13f_2 = tr13f_2.drop_duplicates(subset=['cusip','rdate','mgrno'], keep='first').reset_index(drop=True)
print 'observations after removing duplicates %s' %len(tr13f_2)

# Aggregate shares held by institutional managers per CUSIP-RDATE
inst = pd.DataFrame({'shares': tr13f_2.groupby(['cusip','rdate'])['shares'].sum()})
inst['cusip'] = inst.index.get_level_values(0)
inst['rdate'] = inst.index.get_level_values(1)
inst = inst[['cusip','rdate','shares']].reset_index(drop=True)
print 'observations after aggreation: %s' %len(inst)

# Calculate another useful variable -- number of institutional investors
'''We do not need total shares from CRSP for this variable'''
inst_num = pd.DataFrame({'inst_num': tr13f_2.groupby(['cusip','rdate'])['cusip'].count()})
inst_num['cusip'] = inst_num.index.get_level_values(0)
inst_num['rdate'] = inst_num.index.get_level_values(1)
inst_num = inst_num[['cusip','rdate','inst_num']].reset_index(drop=True)

# Merge with FDATE
'''We need fdate to merge with CRSP to extract the adjusted factor for shares'''
fdate = tr13f_2.drop_duplicates(subset=['cusip','rdate'], keep='first').reset_index(drop=True)
inst_1 = inst.merge(fdate[['cusip','rdate','fdate']], how='left', on=['cusip','rdate'])
inst_1 = inst_1.sort_values(['cusip','rdate']).reset_index(drop=True)

# Merge with CRSP and compute institutional ownership
'''We need to merge with CRSP by mapping CUSIP-FDATE in TR-13F with NCUSIP-DATE in CRSP because CUSIP in TR-13F is historical CUSIP.
   Here, I import the clean CRSP data. Please see 00_Read_data to gain the knowledge how to prepare clean CRSP data'''
crsp = pd.read_hdf(crsp_path+'wrds.h5', 'crspm')
crsp_share = crsp[['ncusip','yr_mo','shrout','cfacshr']].copy()
crsp_share = crsp_share[crsp_share['shrout']>0].reset_index(drop=True)
crsp_share = crsp_share.rename(columns={'ncusip': 'cusip'}) # remember we need NCUSIP from CRSP
crsp_share['total_shares_adj'] = crsp_share['shrout'] * crsp_share['cfacshr'] * 1000 # total shares in CRSP is in 1000
inst_1['yr_mo'] = (inst_1['fdate']/10000).astype('int')*100 + ((inst_1['fdate']/100).astype('int'))%100 # remember we need FDATE from TR-13F
inst_2 = inst_1.merge(crsp_share, how='inner', on=['cusip','yr_mo'])
inst_2['shares_adj'] = inst_2['shares'] * inst_2['cfacshr']
inst_own = inst_2[['cusip','rdate','shares_adj','total_shares_adj']].copy()
inst_own['inst_own'] = inst_own['shares_adj'] / inst_own['total_shares_adj']

# Add number of institutional investors in one table
inst_own = inst_own.merge(inst_num, how='left', on=['cusip','rdate'])
inst_own = inst_own.drop_duplicates(subset=['cusip','rdate'])
inst_own = inst_own.sort_values(['cusip','rdate']).reset_index(drop=True)

# Trimming data
'''delete observations with institutional ownership greater than 100%'''
inst_own_1 = inst_own[inst_own['inst_own']<=1].copy()
inst_own_1 = inst_own_1.sort_values(['cusip','rdate']).reset_index(drop=True)

# Output institutional ownership data
inst_own_1.to_csv(crsp_path+'inst_own.txt', sep='\t', index=False)
