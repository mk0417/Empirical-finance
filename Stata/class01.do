clear // clear data stored in memory
cls // clean results window

// Check current working directory
pwd

// Set up working directory
cd "/Users/ml/Google Drive/af/teaching/database/data"

// Read data from txt file
import delimited msf_2010_2017.txt, clear

// Save data in Stata format
save msf_2010_2017.dta, replace

// Read Stata data
use msf_2010_2017, clear

