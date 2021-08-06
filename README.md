# target_assignee_scripts
For Hsu IPO Innovation project.

This repo contains the scripts for matching target companies to their patents using the assignee data set. The patent_data folder should include assignee.tsv from PatentsView and 
target_firms_with_dup.csv (the original file that Mike provided, renamed). The scripts folder includes a fuzzywuzzy_matching folder which contains the scripts necessary for this matching process.

## To perform matching ##

- First run remove_duplicates_sort.py which removes the duplicates in target_firms_with_dup.csv then sorts the rows alphabetically by target firm name. This script also sorts the rows in assignee.tsv alphabetically. The output files will end up in the outputs folder.
- Run target_assignee_merger.py to match the target firms with assignee firms (with patent count calculated). Output file is in the outputs folder and is called target_matches.csv.

by Kat Wang
katawang@seas.upenn.edu
