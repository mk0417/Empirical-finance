import pandas as pd
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt
import seaborn as sns

sns.set(style='ticks',palette='Set2')


data_dir = '/users/ml/working/risk_aversion_beta/data/'
fig_dir = '/users/ml/working/risk_aversion_beta/figures/'
wrds_dir = '/users/ml/data/wrds/parquet/'


# ---------------------------------
#          Read data
# ---------------------------------

# Monthly CRSP
msf_var = ['permno','cusip','date','ret','prc','shrout', \
    'shrcd','exchcd','ncusip']
msf_raw = pd.read_parquet(wrds_dir+'msf.parquet',columns=msf_var)
len(msf_raw)

msf = msf_raw[(msf_raw['shrcd'].isin([10,11])) \
    &(msf_raw['exchcd'].isin([-2,-1,0,1,2,3]))].copy()
len(msf)

msf = msf.drop_duplicates(['permno','date'])
len(msf)

msf_1 = msf.copy()
msf_1['price'] = msf_1['prc'].abs()
msf_1['mv'] = (msf_1['price']*msf_1['shrout']) / 1000
msf_1['mv'] = np.where(msf_1['mv']>0,msf_1['mv'],np.nan)
msf_1['yrm'] = (msf_1['date']/100).astype(int)
msf_1['calyr'] = (msf_1['yrm']/100).astype(int)
msf_1['month'] = (msf_1['yrm']%100).astype(int)

mv_jun = msf_1[msf_1['month']==6].copy()
mv_jun = mv_jun[['permno','calyr','mv']]
mv_jun.columns = ['permno','calyr','mv_jun']

msf_1['calyr'] = np.where((msf_1['month']>=7)&(msf_1['month']<=12), \
    msf_1['calyr'],msf_1['calyr']-1)
msf_1 = msf_1.sort_values(['permno','yrm']).reset_index(drop=True)
msf_1['mv_l1'] = msf_1.groupby('permno')['mv'].shift(1)
msf_1 = msf_1.merge(mv_jun,how='left',on=['permno','calyr'])
len(msf_1)

# Beta
beta = pd.read_parquet(data_dir+'beta.parquet')
beta = beta.sort_values(['permno','yrm']).reset_index(drop=True)
beta['beta'] = beta.groupby('permno')['beta'].shift(1)
len(beta)

# Risk aversion
aversion = pd.read_excel(data_dir+'ra_index.xlsx',sheet_name='monthly')
aversion = aversion[['Month','rabex2018q7','uncbex2018q7']]
aversion.columns = ['yrm','ra','unc']

# Sentiment
sent = pd.read_excel(data_dir+'bw_sent.xlsx')
sent = sent[['yyyymm','sent']]
sent.columns = ['yrm','sent']

# Disagreement
dis = pd.read_csv(data_dir+'ibes_sum_ltgeps_us.txt.gz', \
    sep='\t',compression='gzip')
len(dis)

dis.columns = dis.columns.str.lower()
dis = dis[(dis['measure']=='EPS')&(dis['fpi']==0)&(dis['usfirm']==1)]
len(dis)

dis = dis.rename(columns={'cusip':'ncusip'})
dis['yrm'] = (dis['statpers']/100).astype(int)
dis_1 = dis[['ncusip','yrm','stdev']] \
    .merge(msf_1[['ncusip','yrm','mv']],how='left',on=['ncusip','yrm'])
dis_1['weight'] = dis_1.groupby('yrm')['mv'] \
    .transform(lambda x: x/x.sum(min_count=1))
dis_1['stdw'] = dis_1['stdev'] * dis_1['weight']
dis_agg = dis_1.groupby('yrm')['stdw'] \
    .sum(min_count=1).to_frame('dis').reset_index()

# Merge time-series data
aversion_1 = aversion.merge(sent,how='left',on='yrm') \
    .merge(dis_agg,how='left',on='yrm')
aversion_1 = aversion_1.sort_values('yrm').reset_index(drop=True)

averplot = aversion_1[['yrm','ra','unc','sent','dis']].copy()
for i in ['ra','unc','sent','dis']:
    averplot[i] = (averplot[i]-averplot[i].mean()) / averplot[i].std()

averplot.index = pd.to_datetime(averplot['yrm'],format='%Y%m')
averplot.index = averplot.index.to_period('M')
del averplot['yrm']
averplot.columns = ['risk aversion','uncertainty','sentiment','disagreement']
averplot.plot(figsize=(8,3.5),lw=0.8)
plt.xlabel('date')
plt.tight_layout()
# plt.savefig(fig_dir+'ra_ts.png',format='png',dpi=600)
plt.show()

aversion_2 = aversion_1.copy()
for i in ['ra','unc','sent','dis']:
    aversion_2[i] = aversion_2[i].shift(1)

aversion_2[['ra','unc','sent','dis']].corr()

aversion_2 = aversion_2[aversion_2['ra'].notnull()]
aversion_2['resid'] = sm.OLS(aversion_2['ra'], \
    sm.add_constant(aversion_2[['unc','sent','dis']])).fit().resid
aversion_2 = aversion_2.sort_values('yrm').reset_index(drop=True)
aversion_2['rarank'] = pd.qcut(aversion_2['ra'],2,labels=False) + 1
aversion_2['rarank1'] = pd.qcut(aversion_2['ra'],3,labels=False) + 1
aversion_2['residrank'] = pd.qcut(aversion_2['resid'],2,labels=False) + 1
aversion_2['residrank1'] = pd.qcut(aversion_2['resid'],3,labels=False) + 1

aversion_ma = aversion_2[['yrm','ra','resid']].copy()
aversion_ma = aversion_ma.sort_values('yrm').reset_index(drop=True)
aversion_ma['rama'] = aversion_ma['ra'].rolling(window=6).mean()
aversion_ma['residma'] = aversion_ma['resid'].rolling(window=6).mean()
aversion_ma['ramarank'] = pd.qcut(aversion_ma['rama'],2,labels=False) + 1
aversion_ma['ramarank1'] = pd.qcut(aversion_ma['rama'],3,labels=False) + 1
aversion_ma['residmarank'] = pd.qcut(aversion_ma['residma'],2,labels=False) + 1
aversion_ma['residmarank1'] = pd.qcut(aversion_ma['residma'],3,labels=False) + 1
aversion_ma = aversion_ma[['yrm','ramarank','ramarank1', \
    'residmarank','residmarank1']]

# Mispricing score (already one-month lag if use my own construction)
# misp = pd.read_parquet(data_dir+'misp_score.parquet')
misp = pd.read_csv('/users/ml/data/personal/misp_score.csv')
misp.columns = ['permno','yrm','mscore']
len(misp)

misp = misp.sort_values(['permno','yrm']).reset_index(drop=True)
misp['mscore'] = misp.groupby('permno')['mscore'].shift(1)

misp['yrm'].min()
misp['yrm'].max()

# Idiosyncratic volatility
ivol = pd.read_parquet(data_dir+'ivol.parquet')
ivol = ivol.sort_values(['permno','yrm']).reset_index(drop=True)
ivol['ivol'] = ivol.groupby('permno')['ivol'].shift(1)

# Maximum daily return
retmax = pd.read_parquet(data_dir+'retmax.parquet')
retmax = retmax.sort_values(['permno','yrm']).reset_index(drop=True)
retmax['retmax'] = retmax.groupby('permno')['retmax'].shift(1)

# Merge everything
msf_2 = msf_1.merge(beta,how='left',on=['permno','yrm']) \
    .merge(aversion_2,how='left',on='yrm') \
    .merge(aversion_ma,how='left',on='yrm') \
    .merge(misp,how='left',on=['permno','yrm']) \
    .merge(ivol,how='left',on=['permno','yrm']) \
    .merge(retmax,how='left',on=['permno','yrm'])
len(msf_2)

msf_2['yrm'].min()
msf_2['yrm'].max()

msf_3 = msf_2[(msf_2['mv_l1'].notnull())&(msf_2['beta'].notnull())].copy()
len(msf_3)

pctl = msf_3[msf_3['exchcd']==1].groupby('yrm')['beta'] \
    .quantile([i/10 for i in range(1,10,1)]).unstack().reset_index()

msf_3 = msf_3.merge(pctl,how='left',on='yrm')
msf_3['betarank'] = np.where(msf_3['beta']<msf_3[0.1],1,np.nan)
for i in range(2,10,1):
    msf_3['betarank'] = np.where((msf_3['beta']>=msf_3[(i-1)/10]) \
        &(msf_3['beta']<msf_3[i/10]),i,msf_3['betarank'])

msf_3['betarank'] = np.where(msf_3['beta']>=msf_3[0.9],10,msf_3['betarank'])
msf_3 = msf_3[msf_3['betarank'].notnull()]
msf_3['weight'] = msf_3.groupby(['yrm','betarank'])['mv_l1'] \
    .transform(lambda x: x/x.sum(min_count=1))
msf_3['retw'] = msf_3['ret'] * msf_3['weight']
msf_3 = msf_3.sort_values(['permno','yrm']).reset_index(drop=True)
len(msf_3)




# ----------------------------------------
#           Long-short spread
# ----------------------------------------

# ---------------------- Raw return: value-weighted ---------------
def nw_t(data,y):
    df = data.copy()
    t = sm.OLS(df[y],np.ones((len(df),1))) \
        .fit(cov_type='HAC',cov_kwds={'maxlags':1},use_t=True).tvalues
    return t

def nw_p(data,y):
    df = data.copy()
    p = sm.OLS(df[y],np.ones((len(df),1))) \
        .fit(cov_type='HAC',cov_kwds={'maxlags':1},use_t=True).pvalues
    return p

# msf_4 = msf_3[(msf_3['yrm']>=192601)&(msf_3['yrm']<=201203)].copy()
# msf_4 = msf_3[(msf_3['yrm']>=192601)&(msf_3['yrm']<=201712)].copy()
msf_4 = msf_3[msf_3['ra'].notnull()].copy()

msf_4['yrm'].min()
msf_4['yrm'].max()

vwport_ts = msf_4.groupby(['yrm','betarank'])['retw'] \
    .sum(min_count=1).unstack()
vwport_ts['diff'] = vwport_ts[1] - vwport_ts[10]

vwport = []
for i in [i for i in range(1,11)]:
    _tmp = vwport_ts[i].mean()
    _tmp_t = nw_t(vwport_ts,i)[0]
    _tmp_p = nw_p(vwport_ts,i)[0]
    vwport.append((_tmp,_tmp_t,_tmp_p))

vwport = pd.DataFrame(vwport,columns=['ret','t','p'], \
    index=[i for i in range(1,11)])
_diff = vwport.loc[1,'ret'] - vwport.loc[10,'ret']
_diff_t = nw_t(vwport_ts,'diff')[0]
_diff_p = nw_p(vwport_ts,'diff')[0]
vwport_diff = pd.DataFrame([(_diff,_diff_t,_diff_p)], \
    columns=['ret','t','p'],index=['diff'])
vwport = pd.concat([vwport,vwport_diff])
vwport['ret'] = vwport['ret'].apply(lambda x: '{:.2f}'.format(x*100))
vwport['ret'] = np.where(vwport['p']<=0.01,vwport['ret']+'***',vwport['ret'])
vwport['ret'] = np.where((vwport['p']>0.01)&(vwport['p']<=0.05), \
    vwport['ret']+'**',vwport['ret'])
vwport['ret'] = np.where((vwport['p']>0.05)&(vwport['p']<=0.1), \
    vwport['ret']+'*',vwport['ret'])
vwport['t'] = vwport['t'].apply(lambda x: '{:.2f}'.format(x))
vwport['t'] = '(' + vwport['t'] + ')'
del vwport['p']
vwport = vwport.T

vwport

x = vwport_ts.merge(aversion)


# -------------------- Alpha: value-weighted ---------------------
def alpha_reg(data,y):
    df = data.copy()
    x = ['mktrf','smb','hml']
    b = sm.OLS(df[y],sm.add_constant(df[x])) \
        .fit(cov_type='HC0',use_t=True).params
    return b[0]

def alpha_t(data,y):
    df = data.copy()
    x = ['mktrf','smb','hml']
    t = sm.OLS(df[y],sm.add_constant(df[x])) \
        .fit(cov_type='HC0',use_t=True).tvalues
    return t[0]

def alpha_p(data,y):
    df = data.copy()
    x = ['mktrf','smb','hml']
    p = sm.OLS(df[y],sm.add_constant(df[x])) \
        .fit(cov_type='HC0',use_t=True).pvalues
    return p[0]

# Market return
ff3 = pd.read_csv('/users/ml/data/ff/ff3_monthly.csv')
for i in ff3.columns[1:]:
    ff3[i] = ff3[i] / 100

vwalpha_ts = vwport_ts.reset_index().merge(ff3,how='inner',on='yrm')
vwalpha = []
for i in [i for i in range(1,11)]:
    _tmp = alpha_reg(vwalpha_ts,i)
    _tmp_t = alpha_t(vwalpha_ts,i)
    _tmp_p = alpha_p(vwalpha_ts,i)
    vwalpha.append((_tmp,_tmp_t,_tmp_p))

vwalpha = pd.DataFrame(vwalpha,columns=['a','t','p'], \
    index=[i for i in range(1,11)])
_diff = vwalpha.loc[1,'a'] - vwalpha.loc[10,'a']
_diff_t = alpha_t(vwalpha_ts,'diff')
_diff_p = alpha_p(vwalpha_ts,'diff')
vwalpha_diff = pd.DataFrame([(_diff,_diff_t,_diff_p)], \
    columns=['a','t','p'],index=['diff'])
vwalpha = pd.concat([vwalpha,vwalpha_diff])
vwalpha['a'] = vwalpha['a'].apply(lambda x: '{:.2f}'.format(x*100))
vwalpha['a'] = np.where(vwalpha['p']<=0.01,vwalpha['a']+'***',vwalpha['a'])
vwalpha['a'] = np.where((vwalpha['p']>0.01)&(vwalpha['p']<=0.05), \
    vwalpha['a']+'**',vwalpha['a'])
vwalpha['a'] = np.where((vwalpha['p']>0.05)&(vwalpha['p']<=0.1), \
    vwalpha['a']+'*',vwalpha['a'])
vwalpha['t'] = vwalpha['t'].apply(lambda x: '{:.2f}'.format(x))
vwalpha['t'] = '(' + vwalpha['t'] + ')'
del vwalpha['p']
vwalpha = vwalpha.T

vwalpha


# ewport_ts = msf_3.groupby(['yrm','betarank'])['ret'].mean().unstack()
# ewport_ts['diff'] = ewport_ts[1] - ewport_ts[10]
# ewalpha_ts = ewport_ts.reset_index().merge(ff3,how='inner',on='yrm')
# for i in [i for i in range(1,11)] + ['diff']:
#     ewalpha_ts[i] = ewalpha_ts[i] - ewalpha_ts['rf']




# -------------------------------------------------------
#        Low vs high risk aversion (double sort)
# -------------------------------------------------------

# ------------------- Raw return: value-weighted --------------------

msf_4.groupby(['yrm','betarank'])['beta'].mean().unstack().mean()

# Aversion threshold: median
ratype = 'rarank'

beta_avg = msf_4.groupby([ratype,'yrm','betarank'])['beta'].mean().unstack()
beta_avg = beta_avg.groupby(level=0).mean().T

beta_avg

vwport_ts_ds = msf_4.groupby([ratype,'yrm','betarank'])['retw'] \
    .sum(min_count=1).unstack()
vwport_ts_ds['diff'] = vwport_ts_ds[1] - vwport_ts_ds[10]

vwport_ts_ds.groupby(level=0).mean()

vwport_ds_plot = vwport_ts_ds.groupby(level=0).mean().iloc[:,:-1].T
fig,(ax1,ax2) = plt.subplots(1,2,figsize=(8,3))
ax1.scatter(beta_avg[1],vwport_ds_plot[1],s=12,c='k',alpha=0.9)
pred_1 = np.poly1d(np.polyfit(beta_avg[1],vwport_ds_plot[1],1))(beta_avg[1])
ax1.plot(beta_avg[1],pred_1,c='k',lw=0.8)
ax1.set_xlabel('beta')
ax1.set_ylabel('return')
ax1.set_title('Panel A: low risk aversion periods')
ax2.scatter(beta_avg[2],vwport_ds_plot[2],12,c='k',alpha=0.9)
pred_2 = np.poly1d(np.polyfit(beta_avg[2],vwport_ds_plot[2],1))(beta_avg[2])
ax2.plot(beta_avg[2],pred_2,c='k',lw=0.8)
ax2.set_xlabel('beta')
ax2.set_ylabel('return')
ax2.set_title('Panel B: high risk aversion periods')
plt.tight_layout()
plt.savefig(fig_dir+'beta_ret_'+ratype+'.png',format='png',dpi=600)
plt.show()


# ------------------- Alpha: value-weighted --------------------
vwalpha_ts_ds = vwport_ts_ds.reset_index().merge(ff3,how='inner',on='yrm')

vwalpha_ds = pd.DataFrame()
for i in [i for i in range(1,11)] + ['diff']:
    _tmp = vwalpha_ts_ds.groupby(ratype).apply(alpha_reg,i).to_frame('a')
    _tmp_t = vwalpha_ts_ds.groupby(ratype).apply(alpha_t,i).to_frame('t')
    _tmp_p = vwalpha_ts_ds.groupby(ratype).apply(alpha_p,i).to_frame('p')
    _tmp = _tmp.join(_tmp_t).join(_tmp_p)
    _tmp['group'] = i
    vwalpha_ds = pd.concat([vwalpha_ds,_tmp])

vwalpha_ts_ds

vwalpha_ds_1 = vwalpha_ds[vwalpha_ds.index==1].copy()
vwalpha_ds_1.index = vwalpha_ds_1['group']
del vwalpha_ds_1['group']
vwalpha_ds_1['a'] = vwalpha_ds_1['a'].apply(lambda x: '{:.2f}'.format(x*100))
vwalpha_ds_1['a'] = np.where(vwalpha_ds_1['p']<=0.01, \
    vwalpha_ds_1['a']+'***',vwalpha_ds_1['a'])
vwalpha_ds_1['a'] = np.where((vwalpha_ds_1['p']>0.01)
    &(vwalpha_ds_1['p']<=0.05),vwalpha_ds_1['a']+'**',vwalpha_ds_1['a'])
vwalpha_ds_1['a'] = np.where((vwalpha_ds_1['p']>0.05)
    &(vwalpha_ds_1['p']<=0.1),vwalpha_ds_1['a']+'*',vwalpha_ds_1['a'])
vwalpha_ds_1['t'] = vwalpha_ds_1['t'].apply(lambda x: '{:.2f}'.format(x))
vwalpha_ds_1['t'] = '(' + vwalpha_ds_1['t'] + ')'
del vwalpha_ds_1['p']
vwalpha_ds_1 = vwalpha_ds_1.T

vwalpha_ds_1

vwalpha_ds_2 = vwalpha_ds[vwalpha_ds.index==2].copy()
vwalpha_ds_2.index = vwalpha_ds_2['group']
del vwalpha_ds_2['group']
vwalpha_ds_2['a'] = vwalpha_ds_2['a'].apply(lambda x: '{:.2f}'.format(x*100))
vwalpha_ds_2['a'] = np.where(vwalpha_ds_2['p']<=0.01, \
    vwalpha_ds_2['a']+'***',vwalpha_ds_2['a'])
vwalpha_ds_2['a'] = np.where((vwalpha_ds_2['p']>0.01)
    &(vwalpha_ds_2['p']<=0.05),vwalpha_ds_2['a']+'**',vwalpha_ds_2['a'])
vwalpha_ds_2['a'] = np.where((vwalpha_ds_2['p']>0.05)
    &(vwalpha_ds_2['p']<=0.1),vwalpha_ds_2['a']+'*',vwalpha_ds_2['a'])
vwalpha_ds_2['t'] = vwalpha_ds_2['t'].apply(lambda x: '{:.2f}'.format(x))
vwalpha_ds_2['t'] = '(' + vwalpha_ds_2['t'] + ')'
del vwalpha_ds_2['p']
vwalpha_ds_2 = vwalpha_ds_2.T

vwalpha_ds_2


# ewport_ts_ds = msf_3.groupby(['rarank','yrm','betarank'])['ret'] \
#     .mean().unstack()
# ewport_ts_ds['diff'] = ewport_ts_ds[1] - ewport_ts_ds[10]
# ewalpha_ts_ds = ewport_ts_ds.reset_index().merge(ff3,how='inner',on='yrm')


# Aversion threshold: top and bottom quartiles
ratype = 'rarank1'

beta_avg = msf_4[msf_4[ratype].isin([1,3])] \
    .groupby([ratype,'yrm','betarank'])['beta'].mean().unstack()
beta_avg = beta_avg.groupby(level=0).mean().T

vwport_ts_ds = msf_4[msf_4[ratype].isin([1,3])] \
    .groupby([ratype,'yrm','betarank'])['retw'] \
    .sum(min_count=1).unstack()
vwport_ts_ds['diff'] = vwport_ts_ds[1] - vwport_ts_ds[10]

vwport_ds_plot = vwport_ts_ds.groupby(level=0).mean().iloc[:,:-1].T
fig,(ax1,ax2) = plt.subplots(1,2,figsize=(8,3))
ax1.scatter(beta_avg[1],vwport_ds_plot[1],s=12,c='k',alpha=0.9)
pred_1 = np.poly1d(np.polyfit(beta_avg[1],vwport_ds_plot[1],1))(beta_avg[1])
ax1.plot(beta_avg[1],pred_1,c='k',lw=0.8)
ax1.set_xlabel('beta')
ax1.set_ylabel('return')
ax1.set_title('Panel A: low risk aversion periods')
ax2.scatter(beta_avg[3],vwport_ds_plot[3],12,c='k',alpha=0.9)
pred_2 = np.poly1d(np.polyfit(beta_avg[3],vwport_ds_plot[3],1))(beta_avg[3])
ax2.plot(beta_avg[3],pred_2,c='k',lw=0.8)
ax2.set_xlabel('beta')
ax2.set_ylabel('return')
ax2.set_title('Panel B: high risk aversion periods')
plt.tight_layout()
plt.savefig(fig_dir+'beta_ret_'+ratype+'.png',format='png',dpi=600)
plt.show()

vwalpha_ts_ds = vwport_ts_ds.reset_index().merge(ff3,how='inner',on='yrm')
vwalpha_ds = pd.DataFrame()
for i in [i for i in range(1,11)] + ['diff']:
    _tmp = vwalpha_ts_ds.groupby(ratype).apply(alpha_reg,i).to_frame('a')
    _tmp_t = vwalpha_ts_ds.groupby(ratype).apply(alpha_t,i).to_frame('t')
    _tmp_p = vwalpha_ts_ds.groupby(ratype).apply(alpha_p,i).to_frame('p')
    _tmp = _tmp.join(_tmp_t).join(_tmp_p)
    _tmp['group'] = i
    vwalpha_ds = pd.concat([vwalpha_ds,_tmp])

vwalpha_ds_1 = vwalpha_ds[vwalpha_ds.index==1].copy()
vwalpha_ds_1.index = vwalpha_ds_1['group']
del vwalpha_ds_1['group']
vwalpha_ds_1['a'] = vwalpha_ds_1['a'].apply(lambda x: '{:.2f}'.format(x*100))
vwalpha_ds_1['a'] = np.where(vwalpha_ds_1['p']<=0.01, \
    vwalpha_ds_1['a']+'***',vwalpha_ds_1['a'])
vwalpha_ds_1['a'] = np.where((vwalpha_ds_1['p']>0.01)
    &(vwalpha_ds_1['p']<=0.05),vwalpha_ds_1['a']+'**',vwalpha_ds_1['a'])
vwalpha_ds_1['a'] = np.where((vwalpha_ds_1['p']>0.05)
    &(vwalpha_ds_1['p']<=0.1),vwalpha_ds_1['a']+'*',vwalpha_ds_1['a'])
vwalpha_ds_1['t'] = vwalpha_ds_1['t'].apply(lambda x: '{:.2f}'.format(x))
vwalpha_ds_1['t'] = '(' + vwalpha_ds_1['t'] + ')'
del vwalpha_ds_1['p']
vwalpha_ds_1 = vwalpha_ds_1.T

vwalpha_ds_1

vwalpha_ds_2 = vwalpha_ds[vwalpha_ds.index==3].copy()
vwalpha_ds_2.index = vwalpha_ds_2['group']
del vwalpha_ds_2['group']
vwalpha_ds_2['a'] = vwalpha_ds_2['a'].apply(lambda x: '{:.2f}'.format(x*100))
vwalpha_ds_2['a'] = np.where(vwalpha_ds_2['p']<=0.01, \
    vwalpha_ds_2['a']+'***',vwalpha_ds_2['a'])
vwalpha_ds_2['a'] = np.where((vwalpha_ds_2['p']>0.01)
    &(vwalpha_ds_2['p']<=0.05),vwalpha_ds_2['a']+'**',vwalpha_ds_2['a'])
vwalpha_ds_2['a'] = np.where((vwalpha_ds_2['p']>0.05)
    &(vwalpha_ds_2['p']<=0.1),vwalpha_ds_2['a']+'*',vwalpha_ds_2['a'])
vwalpha_ds_2['t'] = vwalpha_ds_2['t'].apply(lambda x: '{:.2f}'.format(x))
vwalpha_ds_2['t'] = '(' + vwalpha_ds_2['t'] + ')'
del vwalpha_ds_2['p']
vwalpha_ds_2 = vwalpha_ds_2.T

vwalpha_ds_2



# ---------------------  break -----------------------------------
# --------------------- only need regression results ---------------------

# ---------------------------------------
#       Regression analysis
# ---------------------------------------

# Low and high risk aversion
ratype = 'rarank'

dreg = msf_4.groupby([ratype,'yrm','betarank'])['retw'] \
    .sum(min_count=1).unstack()
dreg['diff'] = dreg[1] - dreg[10]

dreg_1 = dreg.reset_index().merge(ff3,how='inner',on='yrm')
dreg_1['l'] = np.where(dreg_1[ratype]==1,1,0)
dreg_1['h'] = np.where(dreg_1[ratype]==2,1,0)

sm.OLS(dreg_1[1],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[2],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[3],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[4],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[5],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[6],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[7],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[8],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[9],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1[10],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(dreg_1['diff'],dreg_1[['l','h','mktrf','smb','hml']]) \
    .fit(cov_type='HC0',use_t=True).summary()




# ----------------------------------------------
#           Beta-IVOL relation
# ----------------------------------------------

misp = msf_4.copy()
misp['mrank'] = misp.groupby('yrm')['mscore'] \
    .transform(lambda x: pd.qcut(x,5,labels=False)) + 1

beta_ivol = misp[misp['mrank']==5].groupby('yrm')[['beta','ivol']] \
    .corr().reset_index()
beta_ivol = beta_ivol[beta_ivol['level_1']=='beta'][['yrm','ivol']] \
    .reset_index(drop=True)
beta_ivol.columns = ['yrm','bi_corr']
beta_ivol['birank'] = pd.qcut(beta_ivol['bi_corr'],2,labels=False) + 1

ratype = 'residrank'

misp_1 = misp.merge(beta_ivol,how='left',on='yrm')
misp_2 = misp_1.groupby([ratype,'birank','yrm','betarank'])['retw'] \
    .sum(min_count=1).unstack()
misp_2['diff'] = misp_2[1] - misp_2[10]

misp_3 = misp_2.reset_index().merge(ff3,how='inner',on='yrm')

def ra_bi_alpha(port):
    ra_bi = misp_3.groupby([ratype,'birank']) \
        .apply(alpha_reg,port).to_frame('a')
    ra_bi_t = misp_3.groupby([ratype,'birank']) \
        .apply(alpha_t,port).to_frame('t')
    ra_bi_p = misp_3.groupby([ratype,'birank']) \
        .apply(alpha_p,port).to_frame('p')
    ra_bi = ra_bi.join(ra_bi_t).join(ra_bi_p)

    ra_bi['a'] = ra_bi['a'].apply(lambda x: '{:.2f}'.format(x*100))
    ra_bi['a'] = np.where(ra_bi['p']<=0.01, \
        ra_bi['a']+'***',ra_bi['a'])
    ra_bi['a'] = np.where((ra_bi['p']>0.01)
        &(ra_bi['p']<=0.05),ra_bi['a']+'**',ra_bi['a'])
    ra_bi['a'] = np.where((ra_bi['p']>0.05)
        &(ra_bi['p']<=0.1),ra_bi['a']+'*',ra_bi['a'])
    ra_bi['t'] = ra_bi['t'].apply(lambda x: '{:.2f}'.format(x))
    ra_bi['t'] = '(' + ra_bi['t'] + ')'
    del ra_bi['p']
    return ra_bi

ra_bi_alpha(1)

ra_bi_alpha(10)

ra_bi_alpha('diff')




# ----------------------------------------------
#           Betting against beta
# ----------------------------------------------

bab_ts = pd.read_excel(data_dir+'bab.xlsx')
bab_ts['yrm'] = bab_ts['date'].dt.year*100 + bab_ts['date'].dt.month
bab_ts = bab_ts[['yrm','bab']]

bab_ts_ds = bab_ts.merge(aversion_2,how='inner',on='yrm')

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['ra']])) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['resid']])) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['ra','unc']])) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['ra','sent']])) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['ra','dis']])) \
    .fit(cov_type='HC0',use_t=True).summary()

sm.OLS(bab_ts_ds['bab'],sm.add_constant(bab_ts_ds[['ra','unc','sent','dis']])) \
    .fit(cov_type='HC0',use_t=True).summary()



#
