libname db 'D:\Mark\teaching\database';

/*----------------------------
   Merge CRSP and Compustat
----------------------------*/

/*Read CRSP*/
proc import out=crsp_m datafile='D:\Mark\teaching\database\msf_1992_2017' dbms=dta replace;
run;

proc sql;
	create table crsp_m_1 as
	select *
	from crsp_m
	where shrcd in (10,11) and exchcd in (1,2,3);
quit;
proc sort data=crsp_m_1 nodupkey;
	by permno date;
run;
data crsp_m_1;
	set crsp_m_1;
	ret_numeric = ret*1;
	drop ret;
	rename ret_numeric=ret;
run;

/*Create year for merge
Match CRSP return data from July in year t to June in year t+1 with
accounting data in year t-1*/
data crsp_m_1;
	set crsp_m_1;
	yyyymm=int(date/100);
	calyr=int(yyyymm/100);
	month=mod(yyyymm,100);
	if 7<=month<=12 then mergeyr=calyr;
	else if 1<=month<=6 then mergeyr=calyr-1;
run;

/*Read Compustat*/
proc sql;
	create table ag as
	select gvkey,int(datadate/10000) as calyr,calculated calyr+1 as mergeyr,at/at_l1-1 as ag,substr(cusip,1,8) as cusip
	from db.roa
	where cusip ne ''
	order by gvkey,calyr;
quit;
proc means data=ag mean median min max;
	var ag;
run;
proc means data=ag p1 p99 noprint;
	var ag;
	output out=ag_pctl p1=p1 p99=p99;
run;
proc sql noprint;
	select p1 into: p1
	from ag_pctl;
	select p99 into: p99
	from ag_pctl;
quit;
data ag_1;
	set ag;
	where &p1.<=ag<=&p99.;
run;

/*Merge return and asset growth*/
proc sql;
	create table crsp_m_2 as
	select a.*,b.ag
	from crsp_m_1 a join ag_1 b on a.cusip=b.cusip and a.mergeyr=b.mergeyr
	order by permno,date;
quit;

proc reg data=crsp_m_2;
	model ret=ag;
run;
quit;


/*--------------------------------------
   Merge CRSP and Thomson Reuters 13F
--------------------------------------*/

/*Read 13F*/
proc import out=tr13f datafile='D:\Mark\teaching\database\tr13f' dbms=dta replace;
run;

proc sort data=tr13f nodupkey;
	by cusip rdate;
run;

/*Match CRSP return data from July in year t to June in year t+1 with
13F data in June of year t*/
data tr13f;
	set tr13f;
	mergeyr=int(rdate/10000);
	month=mod(int(rdate/100),100);
	if month=6;
run;

proc sql;
	create table crsp_m_3 as
	select a.*,b.numinstowners,b.instown_perc
	from crsp_m_1 a join tr13f b on a.ncusip=b.cusip and a.mergeyr=b.mergeyr
	order by permno,date;
quit;
