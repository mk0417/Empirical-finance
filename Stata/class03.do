clear
cls
set more off

cd "/Users/ml/Google Drive/af/teaching/database/data"

// Read data drop duplicates
import delimited ibes_1976_1990_summ_both.txt, clear
duplicates drop ticker statpers, force

// Check 1-year EPS: use either codebook or count
codebook measure fpi

count if missing(measure)
count if missing(fpi)

// US sample
bysort usfirm: count
keep if usfirm == 1

// Sample selection: keep firms with at least 60 month of numest  
bysort ticker: egen num_month = count(numest)
keep if num_month >= 60

// Generate firmid to check number of unique firm
egen firmid = group(ticker)
order firmid
tabstat firmid, s(max)

// Basic statistics
summ numest meanest stdev
summ numest meanest stdev, d
gen year = int(statpers/10000)
bysort year: summ numest meanest stdev

tabstat numest meanest stdev
help tabstat // check the list of available statistics
tabstat numest meanest stdev, s(n mean sd min p1 median p99 max)
tabstat numest meanest stdev, by(year) s(n mean sd min p1 median p99 max)

// Percentile
centile (meanest), centile(10,20,30,40,50,60,70,80,90)

egen p10 = pctile(meanest), p(10) by(year)
egen p20 = pctile(meanest), p(20) by(year)
egen p30 = pctile(meanest), p(30) by(year)
egen p40 = pctile(meanest), p(40) by(year)
egen p50 = pctile(meanest), p(50) by(year)
egen p60 = pctile(meanest), p(60) by(year)
egen p70 = pctile(meanest), p(70) by(year)
egen p80 = pctile(meanest), p(80) by(year)
egen p90 = pctile(meanest), p(90) by(year)

drop p10-p90
forvalues i = 10(10)90 {
    egen p`i' = pctile(meanest), p(`i') by(year)
}

// Correlation
corr numest meanest stdev
