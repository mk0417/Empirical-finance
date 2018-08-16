clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"


import delimited execucomp_1992_2017.txt, clear

// Any duplicates?
duplicates drop gvkey year execid, force

// Find historical CEO
keep if ceoann == "CEO"

// Find historical CFO
import delimited execucomp_1992_2017.txt, clear
keep if cfoann == "CFO"


import delimited execucomp_1992_2017.txt, clear
// Percentage of female executives
tab1 gender

// Percentage of female CEO
preserve
keep if ceoann == "CEO"
tab1 gender
restore

// Calculate CEO tenure
import delimited execucomp_1992_2017.txt, clear
order gvkey year
keep if ceoann == "CEO"
bysort gvkey execid: egen start_year = min(year)
gen tenure = year - start_year + 1
sort gvkey year

// Number of executive by firm-year
import delimited execucomp_1992_2017.txt, clear
order gvkey year
keep gvkey year execid gender ceoann shrown_excl_opts_pct execrankann
bysort gvkey year: egen n_exec = count(execid)

// Percentage of female by firm-year
gen gender_id = 1 if gender == "FEMALE"
bysort gvkey year: egen n_female = count(gender_id)
gen pct_female = n_female / n_exec

// Percentage of female overtime
preserve
duplicates drop gvkey year, force
tabstat pct_female, by(year) s(mean)
restore

// CEO ownership and top5 executives ownership
replace shrown_excl_opts_pct = shrown_excl_opts_pct / 100
gen ceoown_id = shrown_excl_opts_pct if ceoann == "CEO"
bysort gvkey year: egen ceoown = sum(ceoown_id)
gen top5own_id = shrown_excl_opts_pct if execrankann <= 5
bysort gvkey year: egen top5own = sum(top5own_id)

// Stata returns 0 when sum up all missing Observations
// need to replace with missing for such cases
bysort gvkey year: egen missing_ceoown = count(gvkey) if ceoown_id == .
bysort gvkey year: egen missing_ceoown_1 = max(missing_ceoown)
bysort gvkey year: egen missing_top5own = count(gvkey) if top5own_id == .
bysort gvkey year: egen missing_top5own_1 = max(missing_top5own)

duplicates drop gvkey year, force
replace ceoown = . if n_exec == missing_ceoown_1
replace top5own = . if n_exec == missing_top5own_1
rename year fyear
keep gvkey fyear pct_female ceoown top5own

save execucomp, replace

// ROA
import delimited roa.txt, clear
gen calyr = int(datadate/10000)

//if multiple fiscal year ends in the same year, then keep the most recent one
sort gvkey datadate
bysort gvkey calyr: gen id = _n
bysort gvkey calyr: egen id_max = max(id)
keep if id == id_max

sort gvkey calyr
bysort gvkey: gen at_l1 = at[_n-1]
gen roa = ib / at_l1

// ROE
bysort gvkey: gen seq_l1 = seq[_n-1]
gen roe = ib / seq_l1

// Leverage
gen lev = lt / at

keep gvkey datadate fyear roa roe lev at at_l1 cusip

save roa, replace


/* Regression */

// Merge data
use execucomp, clear
merge 1:1 gvkey fyear using roa
keep if _merge==3
drop _merge

// OLS
reg roa pct_female ceoown
reg roa pct_female top5own

reg roe pct_female ceown
reg roe pct_female top5own

reg lev pct_female ceoown
reg lev pct_female top5own

// Panel regression
xtset gvkey fyear

xtreg roa pct_female ceoown, fe
xtreg roa pct_female top5own, fe

xtreg roe pct_female ceoown, fe
xtreg roe pct_female top5own, fe

xtreg lev pct_female ceoown, fe
xtreg lev pct_female top5own, fe
