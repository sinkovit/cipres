# Program: cipres_data_parse 
#
# Description: Standalone Python program to parse data files uploaded
# to CIPRES gateway. Currently configued to handle BEAST, BEAST2 and
# Migrate input files, but will be extended to other file formats
#
# Note that all files are opened with universal newlines support
# ('rU') so that we can handle files created using the Linux, Windows
# and Mac formats
#
# Author: Robert Sinkovits, SDSC
#
# Usage: cipres_data_parse [filename] 

import re
import sys
file_name = sys.argv[1]

def process_beast(file_name):

    # Process BEAST files and return following
    #
    #    Data type (nucleotide or amino acid)
    #    Codon file (True or False)
    #    Number of partitions
    #    Number of patterns

    # Initialize results
    data_type       = 'unknown'
    is_codon        = False
    partition_count = 0
    pattern_count   = 0

    # Define the regex that will be used to identify
    # and parse the dataType, npatterns and codon lines
    regex_datatype = '.*alignment.*data[tT]ype\s*=\s*"'
    regex_patterns = '.*npatterns\s*=\s*'
    regex_codon    = 'codon'

    # Compile the regex. Probably doesn't make a performance difference
    # since python will cache recently used regex, but doesn't hurt
    cregex_datatype = re.compile('.*alignment.*data[tT]ype\s*=\s*"')
    cregex_patterns = re.compile('.*npatterns\s*=\s*')
    cregex_codon    = re.compile('codon')

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.rstrip()

            # Process the dataType lines
            if cregex_datatype.search(line):
                line = re.sub(regex_datatype, '', line)
                line = re.sub('".*', '', line)
                data_type = re.sub('\s*', '', line)

            # Process the lines that list number of patterns
            # Increment pattern and partition counts
            if cregex_patterns.search(line):
                line = re.sub(regex_patterns, '', line)
                line = re.sub('\D.*', '', line)
                pattern_count   += int(line)
                partition_count += 1
                    
            # Look for lines that contain the string "codon"
            if cregex_codon.search(line):
                is_codon = True

    return data_type, is_codon, partition_count, pattern_count

def process_beast2(file_name):

    # Process BEAST2 files and return following
    #
    #    Number of partitions

    # Partition count is determined from the number of <distribution
    # ...> </distribution> pairs appearing AFTER the tag starting with
    # <distribution id="likelihood"

    # Initialize results
    partition_count = 0
    start_counting = False

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.rstrip()
            
            # Look for the starting line
            if line.find('<distribution id="likelihood"') >= 0:
                start_counting = True
                continue
                
            # Start counting partitions
            if start_counting and line.find('<distribution') >= 0 and line.find('/>') < 0:
                partition_count += 1

    return partition_count

def process_migrate_parm(file_name):

    # Process Migrate parmfile and return following
    #
    #    Number of replicates

    # Replicate count is determined from the line 
    # replicate=< NO | YES:<VALUE | LastChains> >

    # Initialize replicates to 1
    replicates = 1

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.rstrip()
            
            # Look for the starting line
            if line.find('replicate=YES') >= 0:
                p1, replicates = line.split(':')
                break

    return replicates


# Determine the input file type
file_type = 'unknown'
with open(file_name, 'rU') as fin:
    for line in fin:
        if line.find('BEAUTi') >= 0:
            file_type = 'beast'
            break
        if line.find('<beast') >= 0 and line.find('version="2.0">') >= 0:
            file_type = 'beast2'
            break
        if line.find('Parmfile for Migrate') >= 0:
            file_type = 'migrate_parm'
            break

# Process BEAST files
if file_type == 'beast':
    data_type, is_codon, partition_count, pattern_count = process_beast(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'data_type=' + data_type + '\n'
    results += 'is_codon=' + str(is_codon) + '\n'
    results += 'partition_count=' + str(partition_count) +'\n'
    results += 'pattern_count=' + str(pattern_count)

# Process BEAST2 files
if file_type == 'beast2':
    partition_count = process_beast2(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'partition_count=' + str(partition_count)

# Process Migrate parmfile
if file_type == 'migrate_parm':
    replicates = process_migrate_parm(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'replicates=' + str(replicates)

print results
