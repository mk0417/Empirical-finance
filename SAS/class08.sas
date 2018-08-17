/*-------------------------------
			CAPM
-------------------------------*/

proc import out=ff3 datafile='D:\Mark\teaching\database\ff_factors.csv' dbms=csv replace;
run;

proc import out=port25 datafile='D:\Mark\teaching\database\25portfolios.csv' dbms=csv replace;
run;
data port25;
	set port25;
	rename small_lobm=ME1_BM1;
	rename small_hibm=ME1_BM5;
	rename big_lobm=ME5_BM1;
	rename big_hibm=ME5_BM5;
run;
proc sort data=port25;
	by date;
run;
proc transpose data=port25 out=port25_1;
	by date;
run;
data port25_1;
	format port;
	set port25_1;
	port=_name_;
	ret=col1;
	drop _name_ col1;
run;
proc sql;
	create table port25_2 as
	select a.*,a.ret-b.rf as retx,b.mktrf,b.smb,b.hml
	from port25_1 a join ff3 b on a.date=b.date
	order by port,date;
quit;
/*before 1965*/
proc means data=port25_2 n mean std noprint;
	where date<196501;
	by port;
	var retx;
	output out=capm_bef_mean n=obs mean=mean std=std;
run;
proc reg data=port25_2 outest=capm_bef_est tableout adjrsq noprint;
	where date<196501;
	by port;
	model retx=mktrf;
run;
quit;
proc sql;
	create table capm_bef as
	select a.port,a.obs,a.mean,a.std,
		b.intercept as alpha 'alpha',b.mktrf as b_mktrf 'b_mktrf',
		c.intercept as t_alpha 't_alpha',c.mktrf as t_mktrf 't_mktrf',b._adjrsq_ as r2_adj
	from capm_bef_mean a
		join capm_bef_est (where=(_type_='PARMS')) b on a.port=b.port
		join capm_bef_est (where=(_type_='T')) c on b.port=c.port
 	order by port;
quit;

/*after 1965*/
proc means data=port25_2 n mean std noprint;
	where date>=196501;
	by port;
	var retx;
	output out=capm_aft_mean n=obs mean=mean std=std;
run;
proc reg data=port25_2 outest=capm_aft_est tableout adjrsq noprint;
	where date>=196501;
	by port;
	model retx=mktrf;
run;
quit;
proc sql;
	create table capm_aft as
	select a.port,a.obs,a.mean,a.std,
		b.intercept as alpha 'alpha',b.mktrf as b_mktrf 'b_mktrf',
		c.intercept as t_alpha 't_alpha',c.mktrf as t_mktrf 't_mktrf',b._adjrsq_ as r2_adj
	from capm_aft_mean a
		join capm_aft_est (where=(_type_='PARMS')) b on a.port=b.port
		join capm_aft_est (where=(_type_='T')) c on b.port=c.port
 	order by port;
quit;


/*-------------------------------
	Fama-French 3-factor model
-------------------------------*/

proc sql;
	create table port25_2 as
	select a.*,a.ret-b.rf as retx,b.mktrf,b.smb,b.hml
	from port25_1 a join ff3 b on a.date=b.date
	order by port,date;
quit;
proc means data=port25_2 n mean std noprint;
	by port;
	var retx;
	output out=ff3_mean n=obs mean=mean std=std;
run;
proc reg data=port25_2 outest=ff3_est tableout adjrsq noprint;
	by port;
	model retx=mktrf smb hml;
run;
quit;
proc sql;
	create table ff3_a as
	select a.port,a.obs,a.mean,a.std,
		b.intercept as alpha 'alpha',b.mktrf as b_mktrf 'b_mktrf',b.smb as b_smb 'b_smb',b.hml as b_hml 'b_hml',
		c.intercept as t_alpha 't_alpha',c.mktrf as t_mktrf 't_mktrf',c.smb as t_smb 't_smb',c.hml as t_hml 't_hml',
		b._adjrsq_ as r2_adj
	from ff3_mean a
		join ff3_est (where=(_type_='PARMS')) b on a.port=b.port
		join ff3_est (where=(_type_='T')) c on b.port=c.port
 	order by port;
quit;


/*-------------------------------
	Fama-French 5-factor model
-------------------------------*/

proc import out=ff5 datafile='D:\Mark\teaching\database\ff5.csv' dbms=csv replace;
run;

proc sql;
	create table port25_3 as
	select a.*,a.ret-b.rf as retx,b.mktrf,b.smb,b.hml,b.rmw,b.cma
	from port25_1 a join ff5 b on a.date=b.date
	order by port,date;
quit;

proc means data=port25_3 n mean std noprint;
	by port;
	var retx;
	output out=ff5_mean n=obs mean=mean std=std;
run;
proc reg data=port25_3 outest=ff5_est tableout adjrsq noprint;
	by port;
	model retx=mktrf smb hml rmw cma;
run;
quit;
proc sql;
	create table ff5_a as
	select a.port,a.obs,a.mean,a.std,
		b.intercept as alpha 'alpha',b.mktrf as b_mktrf 'b_mktrf',b.smb as b_smb 'b_smb',b.hml as b_hml 'b_hml',
		b.rmw as b_rmw 'b_rmw',b.cma as b_cma 'b_cma',
		c.intercept as t_alpha 't_alpha',c.mktrf as t_mktrf 't_mktrf',c.smb as t_smb 't_smb',c.hml as t_hml 't_hml',
		c.rmw as t_rmw 't_rmw',c.cma as t_cma 't_cma',
		b._adjrsq_ as r2_adj
	from ff5_mean a
		join ff5_est (where=(_type_='PARMS')) b on a.port=b.port
		join ff5_est (where=(_type_='T')) c on b.port=c.port
 	order by port;
quit;
