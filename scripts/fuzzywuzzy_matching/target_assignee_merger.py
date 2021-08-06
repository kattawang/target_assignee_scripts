########################################################################################################################
# Target Companies and Assignee Matcher
#
# Kat Wang
# katawang@seas.upenn.edu
#
# Description: matches target firms with their patents
#
########################################################################################################################
import csv
import math
from fuzzywuzzy import fuzz
import re
import time
from wordfreq import word_frequency
import os.path


def remove_common_substrings(str):
    new_str = str.lower()
    # remove parts of the string, must be at the end
    new_str.replace(' holding', '')
    new_str.replace(' holdings', '')
    new_str = re.sub('\ technology$', '', new_str)
    new_str = re.sub('\ technologies$', '', new_str)
    new_str = re.sub('\ institute$', '', new_str)
    new_str = re.sub('\ uk$', '', new_str)
    new_str = re.sub('\ us$', '', new_str)
    new_str = re.sub('\ gmbh$', '', new_str)
    new_str = re.sub('\ co$', '', new_str)
    new_str = re.sub('\ co.$', '', new_str)
    new_str = re.sub('\ grp$', '', new_str)
    new_str = re.sub('\ incorporated', '', new_str)
    new_str = re.sub('\ inc.$', '', new_str)
    new_str = re.sub('\ inc$', '', new_str)
    new_str = re.sub('\ corp.$', '', new_str)
    new_str = re.sub('\ corp$', '', new_str)
    new_str = re.sub('\ ag$', '', new_str)
    new_str = re.sub('\ ltd$', '', new_str)
    new_str = re.sub('\ ltd.$', '', new_str)
    new_str = re.sub('\ ag.$', '', new_str)
    new_str = re.sub('\ limited$', '', new_str)
    new_str = re.sub('\ company$', '', new_str)
    # added
    new_str = re.sub('\ enterprises$', '', new_str)

    return new_str


# start time
start_time = time.ctime()

# load in the files
assignee_file = open('../../outputs/sorted_assignee.tsv', encoding='utf-8-sig')
assignee = csv.DictReader(assignee_file, delimiter="\t")

target_file = open('../../outputs/target_firms.csv', encoding='utf-8-sig')
target = csv.DictReader(target_file, delimiter=",")

# create an output file
output = open('../../outputs/target_matches.csv', 'w',
              newline="\n", encoding='utf-8-sig')
target_matches = csv.writer(output, delimiter=',')
header = ['acq_name', 'target_name',
          'assignee_firm', 'is_common', 'patent_cnt']
target_matches.writerow(header)

# create a files of non-matches
output = open('../../outputs/target_firms_unmatched.csv',
              'w', newline="\n", encoding='utf-8-sig')
non_target_matches = csv.writer(output, delimiter=',')
header = ['firm_ipo_id', 'ipo_firm', 'acq_name', 'target_name', 'target_cusip',
          'date_effective', 'year', 'joint_ven', 'is_ipo_year', 'post_ipo', 'year_before_aft_ipo']
non_target_matches.writerow(header)

output = open('../../outputs/assignee_target_unmatched.tsv',
              'w', newline="\n", encoding='utf-8-sig')
non_assignee_matches = csv.writer(output, delimiter='\t')
header = ['id', 'type', 'firm']
non_assignee_matches.writerow(header)

# count the number of patents per assignee
print('GENERATING PATENT COUNT PER ASSIGNEE')
patent_cnt = {}  # dictionary mapping assignee id to patent counts
# if not os.path.isfile('../patent_data/assignee_firms_patent_count.tsv'):  # first check to see if such a file exists
with open('../../patent_data/patent_assignee.tsv', encoding='utf-8-sig') as patent_assignee_file:
    patent_assignee = csv.DictReader(patent_assignee_file, delimiter="\t")

    # iterate through the patent_assignee file and generate the dictionary
    for row in patent_assignee:
        patent_id = row['patent_id']
        assignee_id = row['assignee_id']

        if assignee_id not in patent_cnt:
            patent_cnt[assignee_id] = 1
        else:
            patent_cnt[assignee_id] += 1

print('COMPLETED')

print('*** TARGET FIRMS and ASSIGNEE INPUT SIZES ***')
# calculate the size of both input files
assignee_size = len([1 for i in assignee])
print('assignee size: ' + str(assignee_size))
assignee_file.seek(0)  # rewind file
assignee.__next__()

target_size = len([1 for i in target])
print('target size: ' + str(target_size) + '\n')
target_file.seek(0)  # rewind file
target.__next__()

# set of target firms to keep track of what has been matched
unmatched_target = set()

for row in target:
    target_firm = row['target_name'].strip()
    unmatched_target.add(target_firm)

target_file.seek(0)  # rewind file
target.__next__()

# stopped here
# count for progress
cnt = 0
previous_percent = 0
curr_letter = '0'  # to allow for firms that start with numbers

for row in assignee:
    # calculate progress
    # if the firm name string is not of length 0, i.e. the patent is listed under a firm and not a name
    if len(row['firm']) != 0:
        percent_complete = math.floor((cnt / assignee_size) * 100)
        if percent_complete > previous_percent:
            print(str(percent_complete) + '% complete')
            previous_percent = percent_complete

        # .strip() removes the white space around the string (some name have spaces after)
        id = row['id'].strip()
        type = row['type'].strip()
        firm = row['firm'].strip()
        found_match = False

        # set the curr_letter as the first letter of this string
        if not firm.lower().startswith(curr_letter):
            curr_letter = firm[0].lower()
            # print(curr_letter)

        for i in target:
            target_firm = i['target_name'].strip()

            if not target_firm.lower().startswith(curr_letter):
                # continue through if we're before the current assignee letter
                if target_firm[0] < curr_letter:
                    continue
                else:
                    break  # if we're after the current assignee letter, break out of loop

            # remove the common substrings
            modified_firm = remove_common_substrings(firm)
            modified_target_firm = remove_common_substrings(target_firm)

            # 1. check that the target string prefixes the assignee string
            # 2. check that the target string first word is in the words of the assignee string
            # 3. check that the target and assignee have string similarity by substring or by similarity of word sets
            if modified_firm.startswith(modified_target_firm) and \
                    re.sub("[^\w]", " ", modified_target_firm).split()[0] in re.sub("[^\w]", " ", modified_firm).split() and \
                    (fuzz.partial_ratio(modified_firm, modified_target_firm) >= 90 or
                     fuzz.token_sort_ratio(modified_firm, modified_target_firm) >= 90):
                print('target: ' + target_firm)
                print('assignee: ' + firm + '\n')
                # print(modified_target_firm)
                # print(modified_firm)
                # print(fuzz.partial_ratio(modified_firm, modified_target_firm))
                # print(fuzz.token_sort_ratio(modified_firm, modified_target_firm))

                is_common = 1
                # check if the aquired firm name is common
                if word_frequency(modified_target_firm, 'en') < 0.000001:
                    is_common = 0

                # write it to the matches output, and record a found match
                if id not in patent_cnt:
                    patent_cnt[id] = 0

                target_matches.writerow(
                    [i['acq_name'].strip(), target_firm, firm, is_common, patent_cnt[id]])

                found_match = True

                # remove from list of unmatched targets
                if target_firm in unmatched_target:
                    unmatched_target.remove(target_firm)

        # if a match isn't found, return it to the "non-matched" pile
        if not found_match:
            non_assignee_matches.writerow([id, type, firm])
        # this rewinds the csv reader
        target_file.seek(0)
        target.__next__()

        cnt += 1

for i in target:
    target_firm = i['target_name'].strip()
    if target_firm in unmatched_target:
        non_target_matches.writerow(
            [i['firm_ipo_id'], i['ipo_firm'], i['acq_name'], i['target_name'], i['target_cusip'],
             i['date_effective'], i['year'], i['joint_ven'], i['is_ipo_year'], i['post_ipo'], i['year_before_aft_ipo']])


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)
