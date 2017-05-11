/*---------------------------------------------------------------------------------------------------
Institutional ownership
    This tutorial is to demonstrate how to calculate institutional ownership using Thomson Reuters
    13F database.
    Institutional ownership is an important variable in many finance fields. For example, it is
    a proxy of limits-to-arbitage, i.e. higher institutional ownership suggests low limits-to-arbitage;
	high institutional ownership indicates higher level of market efficiency because institutional 
	investors are much more rational than individual investors; company disclosure is positively 
	correlated with institutional ownership; the increase of institutional ownership can reduce 
	information asymmetry between managers and outside investors or agency problem.
---------------------------------------------------------------------------------------------------*/

// Read institutional ownership data
clear
import delimited "/users/ml/data/wrds/raw/inst13f_1980_1989.txt"  // change to your folder
save "/users/ml/data/wrds/raw/inst1.dta",replace

clear
import delimited "/users/ml/data/wrds/raw/inst13f_1990_1999.txt"  // change to your folder
save "/users/ml/data/wrds/raw/inst2.dta",replace

clear
import delimited "/users/ml/data/wrds/raw/inst13f_2000_2008.txt"  // change to your folder
save "/users/ml/data/wrds/raw/inst3.dta",replace

clear
import delimited "/users/ml/data/wrds/raw/inst13f_2009_2015.txt"  // change to your folder
save "/users/ml/data/wrds/raw/inst4.dta",replace

clear
cd "/users/ml/data/wrds/raw"  // change to your folder
append using inst1 inst2 inst3 inst4,force
count 

// Keep shares greater than 0 and delete missing CUSIP
keep if shares>0 & cusip!=""

// Remove duplicates
//TR-13F has multiple FDATEs for a given CUSIP-RDATE-MGRNO and we only keep the first observation in such case
duplicates drop cusip rdate mgrno, force
count

// Aggregate shares held by institutional managers per CUSIP-RDATE
egen shares_sum = total(shares), by(cusip rdate)
egen inst_num = count(shares), by(cusip rdate) // calculate number of institutional investors
duplicates drop cusip rdate, force
gen yr_mo = int(fdate/10000)*100 + mod(int(fdate/100),100) // use FDATE to merge with CRSP
keep cusip rdate yr_mo shares_sum inst_num
sort cusip rdate yr_mo 
save inst_share,replace

// Merge with CRSP and compute institutional ownership
/* We need to merge with CRSP by mapping CUSIP-FDATE in TR-13F with NCUSIP-DATE in CRSP because CUSIP in TR-13F
   is historical CUSIP.
   Here, I import the clean CRSP data. Please see 00_Read_data to gain the knowledge how to prepare clean CRSP data.*/
clear
import delimited "/users/ml/git/crsp_monthly_clean.txt"  // change to your folder
gen shares_total_adj = shrout * cfacshr * 1000 // adjusted shares, unit of share is 1000 in CRSP
gen yr_mo = int(date/10000)*100 + mod(int(date/100),100)
keep if shares_total_adj>0
keep ncusip yr_mo shares_total_adj cfacshr 
rename ncusip cusip // use cusip-ncusip match when merge with CRSP

merge 1:m cusip yr_mo using inst_share 
keep if _merge==3
gen shares_sum_adj = shares_sum * cfacshr
gen inst_own = shares_sum_adj / shares_total_adj
keep cusip rdate shares_sum_adj shares_total_adj inst_own inst_num
keep if inst_own <= 1
order cusip rdate shares_sum_adj shares_total_adj inst_own inst_num
sort cusip rdate
save inst_own,replace

/*Stata is not the best choice for large data. It runs 40 minutes while 7 minutes in Python*/