### MNREGA Data

We scrape data from [MNREGA](https://nrega.nic.in/MGNREGA_new/Nrega_home.aspx).

In particular, we scrape some of the data from [Reports](https://nreganarep.nic.in/netnrega/MISreport4.aspx). We get data for all the years and all the states starting with 2023-2024.

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

#### Scripts & Usage

To scrape R1 data for a specific year, such as 2023, follow these steps:

Run the following command in your terminal:

```
python mnrega_r1.py 2023
```

The CSV files will be saved in the directory `{year}-csv/`.

To scrape R6 data for the same year, repeat the above steps but use the `mnrega_r6.py` script instead:

```
python mnrega_r6.py 2023
```

After scraping the data, you can combine multiple CSV files into a single file using the following command:

```
python combine_csv.py "2023-csv/r1_panchayat_*.csv" output/r1-all-2023.csv
```

This command will combine all the files that match the specified pattern and save the merged data to a single CSV file named `r1-all-2023.csv` in the `output/` directory.

#### Data

The output CSV files are posted at [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZHF9WC)
