### MNREGA Data

We scrape data from [MNREGA](https://nrega.nic.in/netnrega/mgnrega_new/Nrega_home.aspx). 

In particular, we scrape some of the data from [Reports](https://mnregaweb4.nic.in/netnrega/MISreport4.aspx). We get data for all the years and all the states starting with 2023-2024.

We only get two datasets:

1. R1. Category Wise Household/Workers

2. R6.Work Status
	* Work Category Wise
	* **We may collect the following later** 
		* New Work Category Wise 
		* Consolidated New Work Category Wise

For each type of report, we produce the following files with the relevant primary keys:

1. r{1/6}_state.csv --- enumerates all states and includes state level totals
2. r{1/6}_district_{state_name}.csv: 
	* a file for each state enumerates all the districts per state level and district level totals
	* also includes column: state
3. r{1/6}_block_{district}_{state_name}.csv:
	* a file for each district that enumerates all the blocks within a district (state) and block level totals.
	* also includes columns: district, state
4. r{1/6}_panchayat_{block}_{district}_{state_name}.csv:
	* a file for each block that enumerates all the panchayats within a block (within a district within a state) and panchayat level totals.
	* also includes columns: block, district, state

For each state, we aggregate all the files from #4, then join them to #3, then join them to #2. The final dataset is at the state level.
 
