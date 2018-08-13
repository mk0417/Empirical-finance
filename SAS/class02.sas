/* ----------------------------------------------------------------------------
								Data Cleaning
						
"Data cleaning is the process of detecting and correcting (or removing) 
corrupt or inaccurate records from a record set, table, or database and 
refers to identifying incomplete, incorrect, inaccurate or irrelevant 
parts of the data and then replacing, modifying, or deleting the dirty 
or coarse data." -- Wiki

Data cleaning is an important prerequisite before your data analysis. 
Raw data, usually, contains inaccurate and irrevalent observations. 
Your data analysis is not reliable without proper data cleaning.
-----------------------------------------------------------------------------*/


/* Read CRSP

You should consider the following points before you use CRSP:
	Data type
	Stock exchanges
	Share types
	Duplicated observations
	Negative price
	Adjusted price
	Industry 
*/

libname crsp 'D:\Mark\teaching\database';


/* Data type

It is important to identify the type of the data, especially for variable 
with mix type. For example, return or price data should be numeric format. 
However, the variable will be text format if the variable contains both
numeric and string data. For string variable, you cannot perform any 
calculation.

Return data in CRSP contains missing codes, such as 'A', 'B', 'C', etc. 
So the return is in string format after you import raw data from CRSP.

Note: WRDS is written by SAS and SAS is different from other computer
softwares when reading data from WRDS. Even if you can see the letter for
'ret' or 'siccd', they are still numeric in SAS if you download SAS format
directly from WRDS. However, if you download in other formats, for example,
Stata, and then you convert Stata format into SAS format, then variable like
'ret' will be in string format.
*/

/*if you want to remove the missing code, just multiply 1*/
data msf;
	set crsp.msf_2010_2017;
	ret = ret * 1;
	retx = retx * 1;
	siccd = siccd * 1;
	hsiccd = hsiccd * 1;
run;


/* Stock exchanges

Conventionall, we use three main stock exchanges in US market and 'exchcd'
allows us to find out them.

| Stock exchange | exchcd |
|----------------|--------|
| NYSE           | 1      |
| AMEX           | 2      |
| NASDAQ         | 3      |
*/

data msf_1;
	set msf;
	where exchcd in (1,2,3); *equivalently, where exchcd=1 or exchcd=2 or exchcd=3;
run;


/* Share type

CRSP includes different type of securities, for example, common stocks 
and ETFs. Common stocks are most widely used and 'shrcd' = 10 or 11 
can helps us to filter out common shares.
*/

data msf_2;
	set msf_1;
	where shrcd in (10,11); *equivalently, where shrcd=10 or shrcd=11;
run;


/* Duplicated observations

CRSP contains duplicates, therefore, we have to remove them.
*/

proc sort data=msf_2 out=msf_3 nodup;
	by permno date;
run;


/* Negative price

CRSP uses average of bid and ask price to replace price if there is no 
valid closing price for a given data. To distinguish them, CRSP assigns 
negative sign (-) in front of the average of bid and ask price. It does not 
mean the price is negative. Therefore, we need to convert them to 
positive value.
*/

data msf_3;
	set msf_3;
	price = abs(prc);
run;


/* Adjusted price

CRSP returns ('ret') already adjusted dividends and stock splits, and 
it also considers reinvestments effect. However, price in CRSP does not 
consider those corporate events. To adjust price, we can use the formula below:
p_adj = price/ cfacpr
*/

data msf_3;
	set msf_3;
	p_adj = price / cfacpr;
run;


/* Industry

For industry related research, we need to know the industry classification.
'siccd' indicates the industry group.
*/

data msf_4;
	set msf_3;
	where siccd<6000 or siccd>6999;
run;
/*This excludes financial firms. (SIC code for financial firms are between 6000 and 6999)*/
