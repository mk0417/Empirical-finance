/* -----------------------------------  Read data  -------------------------------------------*/
/*Just create a library to read data if we have SAS format data*/

/*Create a library as the working directory so that we can use the data 
and save any further generated data in the folder below*/
libname db 'D:\Mark\teaching\database';


/* ----------------------------------  SAS-WRDS connection  -----------------------------------*/
/*Log in WRDS server*/
%let wrds=wrds.wharton.upenn.edu 4016;
options comamid=TCP remote=WRDS;
signon username=_prompt_;

/*After executing the above three lines, you will see a pop-up window to type your WRDS username and password.
Then you will be able to connect to WRDS*/

/*Create remote library to connect to WRDS data. You can find the remote data path from log window after previous step.
The access permission depends on your institution's subscription. The example below will use annual update CRSP, so the 
remote folder is 'a_stock'. There is also monthly update CRSP and the folder is 'm_stock', but you cannot access to it
if you do not have the subscription in you institution.*/
libname wrds remote '/wrds/crsp/sasdata/a_stock' server=wrds;
/*We can download data directly from WRDS and save in local folder*/
proc sql;
	create table db.sas_retrieve as
	select permno,cusip,date,prc,ret, abs(prc)*vol as dvol
    from wrds.msf
    where'01Jan2016'd<=date<='30Jun2016'd and abs(prc)*vol>1000000000
    order by permno,date;
quit;

/*After you run the above codes, you should see 'sas_retrieve' in your 
local folder: 'D:\Mark\teaching\database' */

/*Sign out and close connection with WRDS*/
signoff;
