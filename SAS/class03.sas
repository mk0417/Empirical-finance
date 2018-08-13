proc import out=ibes datafile='D:\Mark\teaching\database\ibes_1976_1990_summ_both' dbms=dta replace;
run;

/*drop duplicates*/
proc sort data=ibes out=ibes_1 nodupkey;
	by ticker statpers;
run;

/*check if all observations are about 1-year EPS*/
proc print data=ibes_1;
	where fpi ne 1;
run;

/*observations: US vs non-US sample*/
proc sql;
	create table obs_sample as
	select usfirm,count(ticker) as n
	from ibes_1
	group by usfirm;
quit;

/*keep US firms*/
data ibes_us;
	set ibes_1;
	where usfirm=1;
run;

/*keep firms with at least 60 months data*/
proc sql;
	create table ibes_us_1 as
	select *,count(ticker) as n
	from ibes_us
	group by ticker
	having n>=60
	order by ticker,statpers;
quit;

/*number of unique firms*/
proc sql;
	create table ibes_us_unique as
	select distinct ticker
	from ibes_us_1
	order by ticker;
quit;

/*basic statistics*/
proc means data=ibes_us_1 mean median std min max n;
	var numest meanest stdev;
run;

data ibes_us_1;
	set ibes_us_1;
	year=int(statpers/10000);
run;
proc sort data=ibes_us_1;
	by year;
run;
proc means data=ibes_us_1 mean median std min max n;
	by year;
	var numest meanest stdev;
run;

/*percentile*/
proc univariate data=ibes_us_1 noprint;
	by year;
	var meanest;
	output out=ibes_us_pctl pctlpts=10 to 90 by 10 pctlpre=p;
run;
proc sql;
	create table ibes_us_2 as
	select a.ticker,a.statpers,a.meanest,b.*
	from ibes_us_1 a join ibes_us_pctl b on a.year=b.year
	order by ticker,statpers;
quit;

/*correlation*/
proc corr data=ibes_us_1;
	var numest meanest stdev;
run;
