clear
cls
set more off

cd "/Users/ml/Google Drive/af/teaching/database/data"

import delimited g_security.txt, clear
drop if missing(ibtic)
drop if missing(excntry)
gen ticker = ibtic
gen country = excntry
keep if country == "GBR"
keep ticker isin country
duplicates drop ticker, force
save _junk, replace

// Keep UK firms with valid announcement dates
use sue_g, clear
merge m:1 ticker using _junk
keep if !missing(anndats) & !missing(isin)

gen date = anndats
format date %td
gen long date1 = year(date)*10000+month(date)*100+day(date)
duplicates drop isin date1, force
keep isin date1
export delimited earning_uk_list.txt, delimiter(tab) novarnames replace
rm _junk.dta

// Generate I/B/E/S ticker-ISIN link
import delimited g_security.txt, clear
drop if missing(ibtic)
drop if missing(isin)
drop if missing(excntry)
gen ticker = ibtic
gen country = excntry
keep if country == "GBR"
keep ticker isin
duplicates drop isin, force
save ticker_isin_link, replace

// Compustat cumulative abnormal return (CAR) [-59,0]
use uk_abret, clear
keep if evttime>=-59 & evttime<=0
sort isin evtdate date
collapse (sum) car_59b_0 = abret, by(isin evtdate)
save car_uk_59b_0, replace

// Compustat cumulative abnormal return (CAR) [-1,1]
use uk_abret, clear
keep if evttime>=-1 & evttime<=1
sort isin evtdate date
collapse (sum) car_1b_1 = abret, by(isin evtdate)
save car_uk_1b_1, replace

// Compustat cumulative abnormal return (CAR) [1,60]
use uk_abret, clear
keep if evttime>=1 & evttime<=60
sort isin evtdate date
collapse (sum) car_1_60 = abret, by(isin evtdate)
save car_uk_1_60, replace

// Post earnings announcement drift
use sue_g, clear
rename anndats evtdate
rename suescore sue
merge m:1 ticker using ticker_isin_link
keep if _merge == 3 & sue ~= .
drop _merge
merge m:1 isin evtdate using car_uk_59b_0
drop _merge
merge m:1 isin evtdate using car_uk_1b_1
drop _merge
merge m:1 isin evtdate using car_uk_1_60
drop _merge
keep if car_1_60 ~= .
gen year = year(evtdate)
gen qtr = quarter(evtdate)
qui summ sue, d
keep if sue >= r(p1) & sue <= r(p99)

// Quintiles (five groups)
qui {
	forvalues i = 20(20)80 {
		egen p`i' = pctile(sue), p(`i') by(year qtr)
	}
}

gen rank = 1 if sue < p20 & sue ~= .
forvalues i = 40(20)80 {
	local j = `i' - 20
	replace rank = `i'/20 if sue < p`i' & sue >= p`j'
}
replace rank = 5 if sue >= p80 & sue ~= .
drop p20-p80

// pre anncouncement
tabstat car_59b_0, s(n mean sd) by(rank)
// around announcement
tabstat car_1b_1, s(n mean sd) by(rank)
// post announcement
tabstat car_1_60, s(n mean sd) by(rank)

// t test
preserve
keep if rank == 1 | rank == 5
ttest car_1_60, by(rank)
restore


