/*----------------------------------------------------------------------------------
Read data
The data used in this tutorial is from CRSP via WRDS. The sample period is between
1980 to 2016. The data file is named 'crsp_monthly.txt'. I choose the text format
to store the data because:
    1. CUSIP in other formats (eg. excel or csv) will miss leading zeros
    2. The size of text file is smaller than other formats
----------------------------------------------------------------------------------*/

clear

// Read CRSP monthly data   
import delimited "/users/ml/git/crsp_monthly.txt" // change to your data folder
count // show number of observations

// Keep stocks in NYSE, AMEX and NASDAQ
keep if exchcd==1 | exchcd==2 | exchcd==3
count

// Keep common stocks
keep if shrcd==10 | shrcd==11
count

// Remove duplicates
duplicates drop cusip date, force
count

// Sort data
sort cusip date

/*Stata is very convenient for single table*/
