clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"

/* List of M&A events*/
import excel ma.xls, first clear
// Generate 8-digit CUSIP
keep if !missing(AcquirorCUSIP)
gen cusip = AcquirorCUSIP + "10"
// Event list
gen date = DateAnnounced
format date %td
gen long date1 = year(date)*10000+month(date)*100+day(date)
keep if !missing(DateAnnounced) & !missing(TargetNation) & !missing(AcquirorNation)
gen value = real(ValueofTransactionmil)
keep if value >= 100
duplicates drop cusip DateAnnounced, force
keep cusip date1
// Export event list
export delimited ma_list.txt, novarnames delimiter(tab) replace

/*3-day return*/
use ma_abret_3day, clear
duplicates drop cusip evtdate, force
rename evtdate date
rename bhar bhar_3day
keep cusip date bhar_3day
save ma_short, replace

/*1-year return*/
use ma_abret_1yr, clear
duplicates drop cusip evtdate, force
rename evtdate date
rename bhar bhar_1yr
keep cusip date bhar_1yr
save ma_long1yr, replace

/*2-year return*/
use ma_abret_2yr, clear
duplicates drop cusip evtdate, force
rename evtdate date
rename bhar bhar_2yr
keep cusip date bhar_2yr
save ma_long2yr, replace

/*M&A performance*/
import excel ma.xls, first clear
rename DateAnnounced date
gen cusip = AcquirorCUSIP + "10"
keep if !missing(cusip) & !missing(date)
duplicates drop cusip date, force
merge 1:1 cusip date using ma_short
keep if _merge == 3
drop _merge
merge 1:1 cusip date using ma_long1yr
keep if _merge == 3
drop _merge
merge 1:1 cusip date using ma_long2yr
keep if _merge == 3
drop _merge
rename ConsiderationStructure payment
rename TargetPublicStatus public
keep if public == "Public" | public == "Priv."
keep if payment == "CASHO" | payment == "SHARES" | payment == "HYBRID"

// t test by listing status
bysort public: ttest bhar_3day == 0
bysort public: ttest bhar_1yr == 0
bysort public: ttest bhar_2yr == 0

// t test by payment types
bysort payment: ttest bhar_3day == 0
bysort payment: ttest bhar_1yr == 0
bysort payment: ttest bhar_2yr == 0

// listing vs. unlisting
ttest bhar_3day, by(public)
ttest bhar_1yr, by(public)
ttest bhar_2yr, by(public)

// Cash vs. stocks
preserve
keep if payment == "CASHO" | payment == "SHARES"
ttest bhar_3day, by(payment)
ttest bhar_1yr, by(payment)
ttest bhar_2yr, by(payment)
restore

// Cash vs. mixed
preserve
keep if payment == "CASHO" | payment == "HYBRID"
ttest bhar_3day, by(payment)
ttest bhar_1yr, by(payment)
ttest bhar_2yr, by(payment)
restore

// Mixed vs. stocks
preserve
keep if payment == "HYBRID" | payment == "SHARES"
ttest bhar_3day, by(payment)
ttest bhar_1yr, by(payment)
ttest bhar_2yr, by(payment)
restore
