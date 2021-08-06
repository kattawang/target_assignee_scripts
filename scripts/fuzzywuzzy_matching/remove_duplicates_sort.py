########################################################################################################################
# IPO and Assignee Matcher
#
# Kat Wang
# katawang@seas.upenn.edu
#
# Description: removes duplicate target companies from the target column in
# target_firms.csv. Also sorts rows by target name and firm name in alphabetical order
# for target_firms and assignee respectively.
#
########################################################################################################################
import csv
import math
from fuzzywuzzy import fuzz
import re
import time
from wordfreq import word_frequency
import os.path

# start time
start_time = time.ctime()

# load in the files
acq_file = open('../../patent_data/target_firms_with_dup.csv',
                encoding='utf-8-sig')
target_firms_with_dup = csv.DictReader(acq_file, delimiter=",")

# create an intermediary output file for duplicates removed
sans_dup_output = open('../../outputs/target_firms_sans_dup.csv', 'w',
                       newline="\n", encoding='utf-8-sig')
target_firms_sans_dup = csv.writer(sans_dup_output, delimiter=',')
header = ['firm_ipo_id', 'ipo_firm', 'acq_name', 'target_name', 'target_cusip',
          'date_effective', 'year', 'joint_ven', 'is_ipo_year', 'post_ipo',
          'year_before_aft_ipo']
target_firms_sans_dup.writerow(header)

# remove duplicates
print('\nBEGIN REMOVE DUPLICATES\n')
seen = set()
# count duplicates
cnt = 0
for row in target_firms_with_dup:
    target = row['target_name'].strip()
    if target not in seen:
        seen.add(target)
        target_firms_sans_dup.writerow(
            [row['firm_ipo_id'], row['ipo_firm'], row['acq_name'], row['target_name'],
                row['target_cusip'], row['date_effective'], row['year'], row['joint_ven'],
                row['is_ipo_year'], row['post_ipo'], row['year_before_aft_ipo']])
    else:
        cnt += 1
print('Duplicates found:' + str(cnt) + '\n')

# now open the intermediary output file so that the target names without duplicates can be read in
sans_dup_file = open('../../outputs/target_firms_sans_dup.csv',
                     encoding='utf-8-sig')
target_firms_sans_dup = csv.DictReader(
    sans_dup_file, delimiter=",")

# open assignee file to be sorted by firm name as well
assignee_file = open('../../patent_data/assignee.tsv', encoding='utf-8-sig')
assignee = csv.DictReader(assignee_file, delimiter="\t")

# sort the target firms alphabetically
print('\nBEGIN SORT TARGET FIRMS\n')
target_data = sorted(target_firms_sans_dup, key=lambda row: row['target_name'])

# sort the assignee firms alphabetically
print('\nBEGIN SORT ASSIGNEE FIRMS\n')
assignee_data = sorted(assignee, key=lambda row: row['firm'])

# create final target firm output file, sorted without duplicates
target_firms_output = open('../../outputs/target_firms.csv', 'w',
                           newline="\n", encoding='utf-8-sig')
target_firms = csv.writer(target_firms_output, delimiter=',')
header = ['firm_ipo_id', 'ipo_firm', 'acq_name', 'target_name', 'target_cusip',
          'date_effective', 'year', 'joint_ven', 'is_ipo_year', 'post_ipo',
          'year_before_aft_ipo']
target_firms.writerow(header)
for row in target_data:
    target_firms.writerow(
        [row['firm_ipo_id'], row['ipo_firm'], row['acq_name'], row['target_name'], row['target_cusip'],
         row['date_effective'], row['year'], row['joint_ven'], row['is_ipo_year'], row['post_ipo'],
         row['year_before_aft_ipo']])

# create final assignee file sorted by firm
firm_cnt = 0
assignee_output = open('../../outputs/sorted_assignee.tsv', 'w',
                       newline="\n", encoding='utf-8-sig')
sorted_assignee = csv.writer(assignee_output, delimiter='\t')
header = ['id', 'type', 'name_first', 'name_last', 'firm']
sorted_assignee.writerow(header)
for row in assignee_data:
    if len(row['firm']) != 0:
        sorted_assignee.writerow(
            [row['id'], row['type'], row['name_first'], row['name_last'], row['firm']])
        firm_cnt += 1
print('Firm Assignee Count (not under name):' + str(firm_cnt) + '\n')
# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)
