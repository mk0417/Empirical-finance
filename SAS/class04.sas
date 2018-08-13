/*=============================
		Transpose data
=============================*/

libname ds 'D:\Mark\teaching\database\';

/*Read data*/
proc import out=asset datafile='D:\Mark\teaching\database\datastream_data.xlsx' dbms=xlsx replace;
sheet='asset';
run;

/*Transpose*/
proc transpose data=asset out=asset_1;
	by code;
	var _all_;
run;

/*Cleaning*/
data ds.asset_2;
	set asset_1;
	isin=substr(_name_,1,12);
	year=code;
	asset=col1*1;
	if _name_ ne 'Code';
	keep isin year asset;
run;
proc sort data=ds.asset_2;
	by isin year;
run;
proc export data=ds.asset_2 outfile='D:\Mark\teaching\database\datastream_asset_sas.dta' dbms=dta replace;
run;
