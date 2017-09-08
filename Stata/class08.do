clear 
clear matrix
set more off
cls

cd "~/LUBS/PhD data management/data/"

// Clean data
use msf_raw
keep if inlist(exchcd,1,2,3) & inlist(shrcd,10,11)
gen yrm = mofd(mdy(mod(int(date/100),100),mod(date,100),int(date/10000)))
format yrm %tm
duplicates drop permno yrm, force
gen ret1 = real(ret)
drop ret
gen ret = ret1
drop ret1
gen mv = (abs(prc)*shrout) / 1000 // generate market value
keep permno yrm ret mv
gen logret = log(1+ret) // generate log return
order permno yrm
sort permno yrm
tsset permno yrm, monthly // declare panel data 

// Define past winner and loser stocks
// Generate lag returns from t-2 to t-6 (skipping t-1)
forvalues i=2/6 {
	gen ret_l`i' = l`i'.ret
} 
forvalues i=2/6 {
	gen logret_l`i' = l`i'.logret
}
egen n_pre_nomiss = rownonmiss(ret_l2-ret_l6) // count number of past month with valid return
foreach i of varlist ret_l2-ret_l6 {
	replace `i' = 0 if missing(`i') 
} // replace missing lag simple return with 0

// Compute past 6-month return
gen pre6 = (1+ret_l2)*(1+ret_l3)*(1+ret_l4)*(1+ret_l5)*(1+ret_l6) - 1
egen pre6log = rsum(logret_l2-logret_l6) 
replace pre6log = exp(pre6log) - 1
replace pre6 = . if n_pre_nomiss < 4 // require at least 4 month to compute past return
replace pre6log = . if n_pre_nomiss < 4

// Compute average of post 6-month return
forvalues i = 0/5 {
	gen ret_f`i' = f`i'.ret
}
egen n_post_nomiss = rownonmiss(ret_f0-ret_f5)
egen post6 = rsum(ret_f0-ret_f5)
replace post6 = post6 / 6
replace post6 = . if n_post_nomiss < 6
drop ret_l2-ret_l6 logret_l2-logret_l6 ret_f0-ret_f5 n_pre_nomiss n_post_nomiss

// Rank stock into deciles (10 groups)
// In each month, generate percentiles based on past 6-month return
keep if !missing(pre6) & !missing(post6)
sort permno yrm
qui {
	forvalues i = 10(10)90 {
		egen p`i' = pctile(pre6), p(`i') by(yrm)
	}
}

// Allocate stocks into deciles based on past 12-month return
// winner is decile 10 and loser is decile 1
gen pre6_decile = 1 if pre6 < p10 & pre6 ~= .
forvalues i = 20(10)90 {
	local j = `i' - 10
	replace pre6_decile = `i'/10 if pre6 < p`i' & pre6 >= p`j' & pre6 ~= .
}
replace pre6_decile = 10 if pre6 >= p90 & pre6 ~= .
drop p10-p90

// Store number of observations for each portfolio
count if pre6_decile == 1 // count number of stock in decile 1
mat obs = r(N) // save num of stock in decile 1 in matrix
// For loop to save number of stock in the rest of deciles
forvalues i = 2/10 {
	count if pre6_decile == `i'
	mat obs = obs\r(N)
}
mat obs = obs\.

// For each decile we calculate cross-section average of post 6-month return in each month
// here we calculate momentum return in each month from 1926m6 to 2016m7
collapse (mean) post6, by(pre6_decile yrm) 
reshape wide post6, i(yrm) j(pre6_decile)
gen mom = post610 - post61 

// Time-series average of decile return and momentum return
// Here we use preserve-restore to get time series data back automatically after calculating 
// portfolio return, because we need time series data to do t-test
preserve
collapse (mean) post61-post610 mom
mkmat post61-post610 mom, mat(port_ret)
mat port_ret = port_ret'
mat rownames port_ret = 1(loser) 2 3 4 5 6 7 8 9 10(winner) mom(10-1)
mat colnames port_ret = ret
restore

// Test significance of momentum return with Newey-West t-value
// adjust first-order autocorrelation
tsset yrm
qui newey post61, lag(1)
mat mom_nw = r(table)
mat mom_nw_t = mom_nw[3,1]
foreach i of varlist post62-post610 mom {
	qui newey `i', lag(1) 
	mat mom_nw = r(table)
	mat mom_nw_t = mom_nw_t\mom_nw[3,1]
}

// Make table and export to Excel
mat port_table = port_ret, mom_nw_t, obs
mat colnames port_table = ret t obs
putexcel set "port_return.xlsx", replace
putexcel B2 = mat(port_table), names
