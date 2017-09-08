clear // clean existing data in memory
clear matrix
set more off // avoid break when displaying results
cls // clean results window

cd "~/LUBS/phd data management/data/" //  change working folder

// Read CRSP monthly file
// Date range: 192512 to 201612
use msf_raw, clear // raw data observations: 4383894
des // describe data

// This is monthly file so we can generate a new variable 'yrm' to indicate yyyymm
gen yrm = mofd(mdy(mod(int(date/100),100),mod(date,100),int(date/10000)))
format yrm %tm

// convert string to numeric
foreach i in siccd dlretx dlret ret retx{
	gen `i'1 = real(`i')
	drop `i'
	gen `i' = `i'1
	drop `i'1		
}

// keep stocks listing in NYSE/NASDAQ/AMEX
keep if inlist(shrcd,10,11) // observations: 3540967
//keep if shrcd==10 | shrcd==11

// keep common shares
keep if inlist(exchcd,1,2,3) // observations: 3486761
//keep if exchcd==1 | exchcd==2 | exchcd==3

// remove duplicated observations
duplicates drop permno yrm, force // observations: 3457818

// deal with delisting return
gen retd = ret
replace retd = dlret if dlstcd >= 200 & !missing(dlstcd)
replace retd = -0.3 if inlist(dlstcd,500,520,580,584) & missing(dlret) 
replace retd = -0.3 if dlstcd>=551 & dlstcd<=574 & missing(dlret)
replace retd = -1 if dlstcd>=200 & dlstcd<551 & dlstcd!=500 & dlstcd!=520 & missing(dlret)
replace retd = -1 if dlstcd>=574 & dlstcd!=580 & dlstcd!=584 & !missing(dlstcd) & missing(dlret)

// compute market value (millions)
replace prc = abs(prc)
gen mv = (prc*shrout) / 1000

// delete stocks with negative market value
drop if mv <= 0 // observations: 3456940

// Save clean CRSP data
sort permno yrm
save msf, replace


/*---------------     A quick overview of CRSP monthly data     ----------------*/
// define a function to count unique identifier
capture program drop identifier_count
program define identifier_count
	while "`1'" != "" {
		preserve
		duplicates drop `1', force
		count
		restore
		macro shift
	}	
end

identifier_count permno cusip ncusip

// number of month
qui: levelsof yrm, local(yrm_list)
local num_month: word count `yrm_list'
di `num_month'

// return distribution plots
graph drop _all
hist ret, normal name(hist1)
qui: su ret, detail
hist ret if ret>=r(p1) & ret<=r(p99), normal name(hist2)
gr combine hist1 hist2


//---------------------------------------------------------------------------------------------
clear // clean existing data in memory
clear matrix
set more off // avoid break when displaying results
cls // clean results window

// Read data from IBES summary
// US one-year ahead EPS forcast
// Raw data is stored in txt format
import delimited "~/data/wrds/raw/ibes_summary_1976_2016.txt" //obs: 1898838

// Remove duplicates
duplicates drop ticker statpers, force //obs: 1896998

// Extract number of analyst at the end of each year
gen year = int(statpers/10000)
gen month = mod(int(statpers/100),100)
keep if month==6

// Distribution of number of analyst in each year
qui: levelsof year, local(year_list)
foreach i in `year_list' {
	_pctile numest, nq(10)
	di `i'
	return list
}



//---------------------------------------------------------------------------------------------
cd "~/LUBS/phd data management/data/" //  change working folder

import excel using "ds_at.xlsx", firstrow clear

foreach i of varlist _all {
	replace `i'=. if `i'==-999
}

reshape long ds, i(Name) j(dscode)
ren Name year
ren ds asset_tot
order dscode 
sort dscode year

