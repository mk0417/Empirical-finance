## Use SAS to connect WRDS
In addition to web query from WRDS website, you can use SAS to connect WRDS cloud to retrieve data.<br>
There are two main advantages:
1. Flexible: you can use SAS language or SQL to do more complex sample selection.
2. Reuseable: you can make adjustments of SAS script and re-run it to update your sample at anytime. 


>For SAS users, this is even efficient for your workflow, because you can do your analysis immediately after you extract data from WRDS.

>For Stata users, you have to transpose SAS data to 
Stata data.

### SAS code example
```sas
/*Remote connect to WRDS server*/
%let wrds = wrds-cloud.wharton.upenn.edu 4016;
options comamid=TCP remote=WRDS;
signon username=_prompt_;

libname crsp remote '/wrds/crsp/sasdata/a_stock' server=wrds; *this is remote library;
libname yourlib 'your_path'; *this is your local library, e.g. d:\data;

/*Method 1: use SAS data step*/
data yourlib.msf_sample;
    set crsp.msf;
    where '1Jan2015'd<=date<='31Dec2016'd;
    keep cusip date ret vol;
run;

/*Method 2: use SQL*/
proc sql;
    create table yourlib.msf_sample_1 as
    select cusip, date, ret, vol
    from crsp.msf
    where '1Jan2015'd<=date<='31Dec2016'd;
quit;

signoff; *disconnect to WRDS server;


/*----------------------------------------------------------------------------------------------------
  For Stata users, the code below can transfer SAS data to Stata data Please change the path where 
  you want to save your data
----------------------------------------------------------------------------------------------------*/

proc export data=yourlib.msf_sample outfile='d:\msf_sample.dta' dbms=dta replace;
run;
```

You will see a pop-up window after you execute the code. Type your WRDS username and password and then you can be authorized.
![alt text](/Users/ml/LUBS/PhD data management/lecture/latex/class01/wrdsuser.png?raw=true)

---
Update: *good news for Stata users* 

WRDS introduced PostgreSQL feature recently and this makes possible for Stata to connect WRDS. But you have to download PostgreSQL driver and configure it before building the connection.
If you want to try, please follow the link below:

<span style='color:blue'>https://www.stata.com/blog/wrds/Stata_WRDS.pdf</span>