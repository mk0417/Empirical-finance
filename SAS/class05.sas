/*-----------------------------
		Compustat Global
-----------------------------*/

proc import out=gsecd datafile='D:\Mark\teaching\database\g_secd.dta' dbms=dta replace;
run;

/* Keep common shares 
   Keep primary issue
   Remove missing fic*/
data gsecd;
	format fic $5.;
	set gsecd;
	where tpci='0' and iid=prirow and fic ne ' ';
run;

/* Number of markets */
proc sql;
	create table market_list as
	select distinct fic
	from gsecd
	order by fic;
quit;

/* Number of years by market */
data gsecd_1;
	set gsecd;
	year=int(datadate/10000);
run;
proc sql;
	create table n_year_by_mkt as
	select fic,min(year) as start_year,max(year) as end_year
	from gsecd_1
	group by fic;
quit;

/* Number of firms by market */
proc sql;
	create table n_firm_by_mkt as
	select fic,count(gvkey) as n
	from 
		(select distinct fic,gvkey
		 from gsecd_1)
	group by fic;
quit;

/* Keep if number of firms is greater than 50 */
proc sql;
	create table gsecd_2 as
	select a.*
	from gsecd_1 a join n_firm_by_mkt b on a.fic=b.fic
	where b.n>50
	order by fic,gvkey;
quit;

/* List all markets */
proc sql;
	create table market_list_1 as
	select distinct fic
	from gsecd_2
	order by fic;
quit;

/* Adjusted price */
data gsecd_3;
	set gsecd_2;
	p_adj = prccd / ajexdi * trfd;
run;


/*-----------------------------
		Bloomberg
-----------------------------*/

proc import out=bb datafile='D:\Mark\teaching\database\bloomberg_data.xlsx' dbms=xlsx replace;
sheet='Sheet3';
run;

proc transpose data=bb out=bb_1;
	by date;
	var _all_;
run;

data bb_2;
	format isin;
	set bb_1;
	where _name_ ne 'date';
	isin = substr(_name_,1,12);
	asset = col1*1;
	keep isin date asset;
run;

proc sort data=bb_2;
	by isin date;
run;
