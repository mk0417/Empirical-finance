clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"



// Read CRSP
use msf_2010_2017, clear

// Show the data and check the data format
br

// Convert format
gen ret_numeric = real(ret)
gen siccd_numeric = real(siccd)

drop ret siccd
rename ret_numeric ret
rename siccd_numeric siccd

// Stock exchanges
keep if inlist(exchcd,1,2,3) // equivalently, keep if exchcd==1 | exchcd==2 | exchcd==3

// Share type
keep if inlist(shrcd,10,11) // equivalently, keep if shrcd==10 | shrcd==11

// Duplicated observations
duplicates drop permno date, force

// Negative price
gen price = abs(prc)

// Adjusted price
gen p_adj = price / cfacpr

// Market value (Million)
gen mv = (price*shrout) / 1000
label var mv "market value"

// Time periods
keep if date>=20140101

// Industry
keep if siccd<6000 | siccd>6999

// Summary statistics
summ ret

summ ret, detail

summ ret if exchcd == 1

bysort exchcd: summ ret

// Convert 8-digit CUSIP to 6-digit CUSIP
gen cusip6 = substr(cusip,1,6)

// Annual return (December to December)
gen year = int(date/10000)
gen month = mod(int(date/100),100)
keep if month == 12
sort permno year
by permno: gen p_lag = p_adj[_n-1]
by permno: gen year_lag = year[_n-1]
gen ret_annual = p_adj/p_lag - 1
gen year_diff = year - year_lag
list permno date p_adj p_lag ret_annual year year_lag year_diff if year_diff>1 & year_diff!=.
replace ret_annual = . if year_diff != 1
list permno date p_adj p_lag ret_annual year year_lag year_diff if year_diff>1 & year_diff!=.
