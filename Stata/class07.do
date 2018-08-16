clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"


/* Merge CRSP and Compustat */

// Read CRSP
import delimited msf_1992_2017.txt, clear
keep if inlist(exchcd,1,2,3) & inlist(shrcd,10,11)

gen ret_numeric = real(ret)
drop ret
rename ret_numeric ret

duplicates drop permno date, force

gen yyyymm = int(date/100)
gen calyr = int(yyyymm/100)
gen month = mod(yyyymm,100)

// Create year for merge
// Match CRSP return data from July in year t to June in year t+1 with
// accounting data in year t-1
gen mergeyr = calyr if month>=7 & month<=12
replace mergeyr = calyr - 1 if month>=1 & month<=6
keep permno date yyyymm ret cusip ncusip mergeyr
sort permno date

save crsp_ret, replace

// Read Compustat
use roa, clear
keep if cusip != ""
gen calyr = int(datadate/10000)
gen mergeyr = calyr + 1
replace cusip=substr(cusip,1,8)
gen ag = at / at_l1 - 1

summ ag, d
keep if ag>=`r(p1)' & ag<=`r(p99)'

keep gvkey datadate ag cusip mergeyr
sort gvkey datadate

save ag, replace

// Merge return with asset growth
use crsp_ret, clear
merge m:1 cusip mergeyr using ag
keep if _merge == 3
drop _merge
sort permno date

reg ret ag

xtset permno date
xtreg ret ag


/* Merge CRSP and Thomson Reuters 13F */

// Read 13F
import delimited tr13f.txt, clear
duplicates drop cusip rdate, force

// Match CRSP return data from July in year t to June in year t+1 with
// 13F data in June of year t
gen mergeyr = int(rdate/10000)
gen month = mod(int(rdate/100),100)
keep if month == 6
rename cusip ncusip
keep ncusip mergeyr numinstowners instown_perc

save tr13f_jun, replace

// Merge return with institutional ownership
use crsp_ret, clear
merge m:1 ncusip mergeyr using tr13f_jun
keep if _merge == 3
drop _merge
