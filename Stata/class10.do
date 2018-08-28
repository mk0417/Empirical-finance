clear
cls
set more off

cd "/Users/ml/Google Drive/af/teaching/database/data"

use rdate, clear

/*US earnings announcement dates*/

// keep US firms
keep if fic == "USA"

// keep stocks listing in NYSE/AMEX/NASDAQ
keep if inlist(exchg,11,12,14)

// delete missing rdq
drop if rdq == .

// convert to 8-digit CUSIP
gen cusip8 = substr(cusip,1,8)

// date format
gen long date1 = year(rdq)*10000+month(rdq)*100+day(rdq)

// save event list
duplicates drop cusip8 date1, force
keep cusip8 date1
export delimited earning_us_list.txt, delimiter(tab) novarnames replace


/*UK earnings announcement dates*/

// country ID
import delimited g_security.txt, clear
drop if missing(ibtic)
drop if missing(excntry)
gen ticker = ibtic
gen country = excntry
keep ticker isin country
duplicates drop ticker, force
save _junk, replace

// keep UK firms with valid announcement dates
use rdate_g, clear
merge m:1 ticker using _junk
keep if country == "GBR" & !missing(anndats_act) & !missing(isin)

gen date = anndats_act
gen long date1 = year(date)*10000+month(date)*100+day(date)
duplicates drop isin date1, force
keep isin date1
export delimited earning_uk_list.txt, delimiter(tab) novarnames replace
rm _junk.dta

