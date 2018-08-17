clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"


/*--------------------------------------
                 CAPM
---------------------------------------*/

// Import FF 3-factors
import delimited "ff_factors.csv", clear
save _junk, replace

// Import 25 (5x5) portfolios formed on size and book-to-market ratio
import delimited "25portfolios.csv", clear
ren smalllobm me1bm1
ren smallhibm me1bm5
ren biglobm me5bm1
ren bighibm me5bm5

// Merge with FF 3-factors
merge 1:1 date using _junk
keep if _merge == 3
drop _merge
mvdecode _all, mv(-99.99 -999)
rm _junk.dta

// Calculate excess return
foreach i of varlist me1bm1-me5bm5 {
	replace `i' = `i' - rf
}

// CAPM and 25 (5x5) portfolios formed on market value and
// book-to-makret ratio (before 1965)
mat capm_25port_bef= J(25,8,0)
mat colnames capm_25port_bef = obs mean std alpha b_mkt t_alpha t_mkt r2_adj
local rnames
local k = 1
forvalues i = 1/5 {
	forvalues j = 1/5 {
		local rnames `rnames' me`i'bm`j'
		qui sum me`i'bm`j' if date < 196501
		mat capm_25port_bef[`k',1] = round(r(N),0.01)
		mat capm_25port_bef[`k',2] = round(r(mean),0.01)
		mat capm_25port_bef[`k',3] = round(r(sd),0.01)
		qui reg me`i'bm`j' mktrf if date < 196501
		mat capm_25port_bef[`k',4] = round(_b[_cons],0.001)
		mat capm_25port_bef[`k',5] = round(_b[mktrf],0.001)
		mat capm_25port_bef[`k',6] = round(_b[_cons]/_se[_cons],0.01)
		mat capm_25port_bef[`k',7] = round(_b[mktrf]/_se[mktrf],0.01)
		mat capm_25port_bef[`k',8] = round(e(r2_a),0.01)
		local ++k
	}
}

mat rownames capm_25port_bef = `rnames'
svmat2 capm_25port_bef, rnames(port) names(col)
twoway (scatter mean b_mkt in 1/25, mlabel(port) xscale(range(0.9 1.9)) xtitle({&beta}) ///
	ytitle("return") subtitle("CAPM: from 1926 to 1964") legend(off)) ///
    (lfit mean b_mkt)

drop obs-port

// CAPM and 25 (5x5) portfolios formed on market value and
// book-to-makret ratio (after 1965)
mat capm_25port_aft= J(25,8,0)
mat colnames capm_25port_aft = obs mean std alpha b_mkt t_alpha t_mkt r2_adj
local rnames
local k = 1
forvalues i = 1/5 {
	forvalues j = 1/5 {
		local rnames `rnames' me`i'bm`j'
		qui sum me`i'bm`j' if date >= 196501
		mat capm_25port_aft[`k',1] = round(r(N),0.01)
		mat capm_25port_aft[`k',2] = round(r(mean),0.01)
		mat capm_25port_aft[`k',3] = round(r(sd),0.01)
		qui reg me`i'bm`j' mktrf if date >= 196501
		mat capm_25port_aft[`k',4] = round(_b[_cons],0.001)
		mat capm_25port_aft[`k',5] = round(_b[mktrf],0.001)
		mat capm_25port_aft[`k',6] = round(_b[_cons]/_se[_cons],0.01)
		mat capm_25port_aft[`k',7] = round(_b[mktrf]/_se[mktrf],0.01)
		mat capm_25port_aft[`k',8] = round(e(r2_a),0.01)
		local ++k
	}
}

mat rownames capm_25port_aft = `rnames'
svmat2 capm_25port_aft, rnames(port) names(col)
twoway (scatter mean b_mkt in 1/25, mlabel(port) xscale(range(0.8 1.5)) xtitle({&beta}) ///
	ytitle("return") subtitle("CAPM: from 1965 to 2017") legend(off)) (lfit mean b_mkt)

drop obs-port


/*--------------------------------------
       Fama-French 3-factor model
---------------------------------------*/

// Fama-French 3-factor model and 25 (5x5) portfolios formed on market value
// and book-to-makret ratio
mat ff3_25port = J(25,12,0)
mat colnames ff3_25port = obs mean std alpha b_mkt b_smb b_hml t_alpha t_mkt t_smb t_hml r2_adj
local rnames
local k = 1
forvalues i = 1/5 {
	forvalues j = 1/5 {
		local rnames `rnames' me`i'bm`j'
		qui sum me`i'bm`j' if date >= 196501
		mat ff3_25port[`k',1] = round(r(N),0.01)
		mat ff3_25port[`k',2] = round(r(mean),0.01)
		mat ff3_25port[`k',3] = round(r(sd),0.01)
		qui reg me`i'bm`j' mktrf smb hml if date >= 196501
		mat ff3_25port[`k',4] = round(_b[_cons],0.001)
		mat ff3_25port[`k',5] = round(_b[mktrf],0.001)
		mat ff3_25port[`k',6] = round(_b[smb],0.001)
		mat ff3_25port[`k',7] = round(_b[hml],0.001)
		mat ff3_25port[`k',8] = round(_b[_cons]/_se[_cons],0.01)
		mat ff3_25port[`k',9] = round(_b[mktrf]/_se[mktrf],0.01)
		mat ff3_25port[`k',10] = round(_b[smb]/_se[smb],0.01)
		mat ff3_25port[`k',11] = round(_b[hml]/_se[hml],0.01)
		mat ff3_25port[`k',12] = round(e(r2_a),0.01)
		local ++k
	}
}

mat rownames ff3_25port = `rnames'
svmat2 ff3_25port, rnames(port) names(col)
qui sum mktrf
local mkt_mean = r(mean)
qui sum smb
local smb_mean = r(mean)
qui sum hml
local hml_mean = r(mean)
gen estret = b_mkt*`mkt_mean' + b_smb*`smb_mean' + b_hml*`hml_mean'
twoway (scatter mean estret in 1/25, mlabel(port) xscale(range(0.4 1.3)) xtitle("estimated return") ///
	ytitle("realized return") subtitle("FF3: from 1965 to 2017") legend(off)) (lfit mean estret)

drop obs-estret


/*--------------------------------------
       Fama-French 5-factor model
---------------------------------------*/

// Import FF 5-factors
import delimited "ff5.csv", clear
save _junk, replace

// Import 25 (5x5) portfolios formed on size and book-to-market ratio
import delimited "25portfolios.csv", clear
ren smalllobm me1bm1
ren smallhibm me1bm5
ren biglobm me5bm1
ren bighibm me5bm5
// Merge with FF 3-factors
merge 1:1 date using _junk
keep if _merge == 3
drop _merge
mvdecode _all, mv(-99.99 -999)
rm _junk.dta

// Calculate excess return
foreach i of varlist me1bm1-me5bm5 {
	replace `i' = `i' - rf
}

// Fama-French 5-factor model and 25 (5x5) portfolios formed on market value
// and book-to-makret ratio
mat ff5_25port = J(25,16,0)
mat colnames ff5_25port = obs mean std alpha b_mkt b_smb b_hml b_rmw b_cma t_alpha t_mkt t_smb t_hml t_rmw t_cma r2_adj
local rnames
local k = 1
forvalues i = 1/5 {
	forvalues j = 1/5 {
		local rnames `rnames' me`i'bm`j'
		qui sum me`i'bm`j' if date >= 196501
		mat ff5_25port[`k',1] = round(r(N),0.01)
		mat ff5_25port[`k',2] = round(r(mean),0.01)
		mat ff5_25port[`k',3] = round(r(sd),0.01)
		qui reg me`i'bm`j' mktrf smb hml rmw cma if date >= 196501
		mat ff5_25port[`k',4] = round(_b[_cons],0.001)
		mat ff5_25port[`k',5] = round(_b[mktrf],0.001)
		mat ff5_25port[`k',6] = round(_b[smb],0.001)
		mat ff5_25port[`k',7] = round(_b[hml],0.001)
		mat ff5_25port[`k',8] = round(_b[rmw],0.001)
		mat ff5_25port[`k',9] = round(_b[cma],0.001)
		mat ff5_25port[`k',10] = round(_b[_cons]/_se[_cons],0.01)
		mat ff5_25port[`k',11] = round(_b[mktrf]/_se[mktrf],0.01)
		mat ff5_25port[`k',12] = round(_b[smb]/_se[smb],0.01)
		mat ff5_25port[`k',13] = round(_b[hml]/_se[hml],0.01)
		mat ff5_25port[`k',14] = round(_b[rmw]/_se[rmw],0.01)
		mat ff5_25port[`k',15] = round(_b[cma]/_se[cma],0.01)
		mat ff5_25port[`k',16] = round(e(r2_a),0.01)
		local ++k
	}
}

mat rownames ff5_25port = `rnames'
svmat2 ff5_25port, rnames(port) names(col)
qui sum mktrf
local mkt_mean = r(mean)
qui sum smb
local smb_mean = r(mean)
qui sum hml
local hml_mean = r(mean)
qui sum rmw
local rmw_mean = r(mean)
qui sum cma
local cma_mean = r(mean)
gen estret = b_mkt*`mkt_mean' + b_smb*`smb_mean' + b_hml*`hml_mean' + b_rmw*`rmw_mean' + b_cma*`cma_mean'
twoway (scatter mean estret in 1/25, mlabel(port) xscale(range(0.3 1.1)) xtitle("estimated return") ///
	ytitle("realized return") subtitle("FF5: from 1965 to 2017") legend(off)) (lfit mean estret)

drop obs-estret
