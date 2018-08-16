libname db 'D:\Mark\teaching\database';

/*-----------------------------
		Execucomp
-----------------------------*/

proc import out=execucomp datafile='D:\Mark\teaching\database\execucomp_1992_2017.dta' dbms=dta replace;
run;

/*check duplicates*/
proc sort data=execucomp out=execucomp_1 nodupkey;
	by gvkey year execid;
run;

/*historical CEO*/
data ceo;
	set execucomp_1;
	where ceoann='CEO';
run;

/*historical CFO*/
data cfo;
	set execucomp_1;
	where cfoann='CFO';
run;

/*percent of female executives*/
proc freq data=execucomp_1;
	tables gender;
run; 

/*percent of female CEO*/
proc freq data=ceo;
	tables gender;
run;

/*CEO tenure*/
proc sort data=ceo;
	by gvkey year;
run;
proc sql;
	create table ceo_1 as
	select gvkey,year,exec_fullname,execid,min(year) as start_year,year-calculated start_year+1 as tenure
	from ceo
	group by gvkey,execid
	order by gvkey,year;
quit;

/*number of executives by firm-year*/
proc sql;
	create table execucomp_2 as
	select *,count(gvkey) as n_exec
	from execucomp_1
	group by gvkey,year;
quit;

/*percentage of female by firm-year*/
data execucomp_2;
	set execucomp_2;
	if gender='FEMALE' then gender_id=1;
run;
proc sql;
	create table execucomp_3 as
	select *,count(gender_id) as n_female,calculated n_female/n_exec as pct_female
	from execucomp_2
	group by gvkey,year;
quit;

/*percentage of female overtime*/
proc sql;
	create table pct_female as
	select distinct year,avg(pct_female) as pct_female
	from 
		(select distinct gvkey,year,pct_female
		 from execucomp_3)
	group by year;
quit;

/*CEO ownership and top5 ownership*/
data execucomp_4;
	set execucomp_3;
	shrown_excl_opts_pct=shrown_excl_opts_pct/100;
	if ceoann='CEO' then ceoown_id=shrown_excl_opts_pct;
	if execrankann<=5 then top5own_id=shrown_excl_opts_pct;
run;
proc sql;
	create table execucomp_5 as
	select *,sum(ceoown_id) as ceoown,sum(top5own_id) as top5own
	from execucomp_4
	group by gvkey,year;
quit;
proc sql;
	create table execucomp_6 as
	select distinct gvkey,year,pct_female,ceoown,top5own
	from execucomp_5
	order by gvkey,year;
quit;


/*ROA*/
proc import out=roa datafile='D:\Mark\teaching\database\roa_raw.dta' dbms=dta replace;
run;
data roa;
	set roa;
	calyr=int(datadate/10000);
run;
*if multiple fiscal year ends in the same year, then keep the most recent one;
proc sort data=roa;
	by gvkey datadate;
run;
data roa_1;
	set roa;
	by gvkey calyr;
	if last.calyr;
run;

proc sort data=roa_1;
	by gvkey calyr;
run;
data roa_2;
	set roa_1;
	at_l1=lag(at);
	seq_l1=lag(seq);
	by gvkey;
	if first.gvkey then do;
		at_l1=.;
		seq_l1=.;
	end;
run;
data db.roa;
	set roa_2;
	roa=ib/at_l1;
	roe=ib/seq_l1;
	lev=lt/at;
run;

/*Regression*/
*Merge required data;
proc sql;
	create table db.execucomp as
	select a.gvkey,b.fyear,a.pct_female,a.ceoown,a.top5own,b.roa,b.roe,b.lev
	from execucomp_6 a join db.roa b on a.gvkey=b.gvkey and a.year=b.fyear
	order by gvkey,datadate;
quit;
proc sql;
	create table execucomp_7 as
	select *
	from db.execucomp
	group by gvkey
	having count(ceoown)>1;
quit;

*OLS;
proc reg data=db.execucomp;
	model roa=pct_female ceoown;
run;
quit;
proc reg data=db.execucomp;
	model roa=pct_female top5own;
run;
quit;
proc reg data=db.execucomp;
	model roe=pct_female ceoown;
run;
quit;
proc reg data=db.execucomp;
	model roe=pct_female top5own;
run;
quit;
proc reg data=db.execucomp;
	model lev=pct_female ceoown;
run;
quit;
proc reg data=db.execucomp;
	model lev=pct_female top5own;
run;
quit;

*Panel regression;
proc panel data=execucomp_7;
	id gvkey fyear;
	model roa=pct_female ceoown / fixone;
quit;


