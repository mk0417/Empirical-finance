libname db 'D:\Mark\teaching\database';

%let wrds=wrds.wharton.upenn.edu 4016;
options comamid=TCP remote=WRDS;
signon username=_prompt_;

libname wrds remote '/wrds/comp/sasdata/global/security' server=wrds;
proc sql;
	create table db.g_security as
	select *
    from wrds.g_security;
quit;

signoff;

proc export data=db.g_security outfile='D:\Mark\teaching\database\g_security.txt' dbms=tab replace;
run;
