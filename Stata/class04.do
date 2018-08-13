clear
set more off
cls

cd "/Users/ml/Google Drive/af/teaching/database/data"

// Import firm total asset
import excel using datastream_data, sheet("asset_1") first clear
rename Code year

// Reshape wide to long
reshape long var, i(year) j(firmid)
rename var asset
save datastream_asset,replace

// Import firm list and merge firm total asset
import excel using datastream_data, sheet("firm_list") first clear
merge 1:m firmid using datastream_asset
drop _merge
save datastream_asset,replace

// Import fiscal year end and reshape
import excel using datastream_data, sheet("fyend_1") first clear
rename Code year
reshape long var, i(year) j(firmid)
rename var fyend

// Merge firm total asset
merge 1:1 firmid year using datastream_asset
drop _merge firmid
order isin year
sort isin year
save datastream_data, replace
