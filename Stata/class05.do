clear
set more off
cls


cd "/Users/ml/Google Drive/af/teaching/database/data"


// ------------------------------
//      Compustat Global
// ------------------------------

import delimited g_secd.txt, clear

/* Keep common shares */
keep if tpci == "0"

/* Keep primary issue */
keep if iid == prirow

/* Remove missing fic */
drop if missing(fic)

/* Number of markets */
codebook fic

/* Number of years by market */
gen year = int(datadate/10000)
bysort fic: summ year
tabstat year, by(fic) s(min max)

/* Number of firms by market */
// method 1:
bysort fic gvkey: gen nfirm = _n
bysort fic: count if nfirm == 1
// method 2:
preserve
keep if nfirm == 1
tabstat gvkey, by(fic) s(count)
restore

/* Keep if number of firms is greater than 50 */
bysort fic gvkey: gen nfirm1 = nfirm==1
bysort fic: egen n=sum(nfirm1)
keep if n>50
codebook fic

/* List all markets */
qui levelsof fic, local(fic_list)
foreach i of local fic_list {
    di "`i'""
}

/* Adjusted price */
gen p_adj = prccd / ajexdi * trfd

order fic gvkey datadate
sort fic gvkey datadate



// ------------------------------
//         Bloomberg
// ------------------------------

import excel bloomberg_data, sheet("Sheet3") firstrow clear

local c = 1
foreach i of varlist GB00B1XZS820Equity-GB00B1KJJ408Equity {
    rename `i' firm`c'
    local c = `c'+1
}

ds, has(type string)
return list
drop `r(varlist)'

reshape long firm, i(date) j(firmid)
rename firm assets
order firmid date
sort firmid date
