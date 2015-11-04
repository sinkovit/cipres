# Program: cipres_data_parse 
#
# Description: Standalone Python program to parse data files uploaded
# to CIPRES gateway. Currently configued only to handle BEAUTi files,
# but will be extended to other file formats
#
# Author: Robert Sinkovits, SDSC
#
# Usage: cipres_data_parse [filename] 

import re
import sys
filename = sys.argv[1]

def process_beauti(filename):

    # Process BEAUTi format files and return following
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

    # Define the regular expressions that will be used to identify
    # and parse the dataType, npatterns and codon lines
    regex_datatype = '.*alignment.*data[tT]ype\s*=\s*"'
    regex_patterns = '.*npatterns\s*=\s*'
    regex_codon    = 'codon'

    with open(filename, 'r') as fin:
        for line in fin:
            line = line.rstrip()

            # Process the dataType lines
            if re.search(regex_datatype, line):
                line = re.sub(regex_datatype, '', line)
                data_type = re.sub('".*', '', line)

            # Process the lines that list number of patterns
            # Increment pattern and partition counts
            if re.search(regex_patterns, line):
                line = re.sub(regex_patterns, '', line)
                line = re.sub('\D.*', '', line)
                pattern_count   += int(line)
                partition_count += 1
                    
            # Look for lines that contain the string "codon"
            if re.search(regex_codon, line):
                is_codon = True

    print 'data type:            ', data_type
    print 'Is codon file:        ', is_codon
    print 'number of partitions: ', partition_count
    print 'number of patterns:   ', pattern_count
    return data_type, is_codon, partition_count, pattern_count


# Determine the input file type
filetype = 'unknown'
with open(filename, 'r') as fin:
    for line in fin:
        if line.find('BEAUTi') >= 0:
            filetype = 'beauti'
            break

print 'file type: ', filetype

# Loop over records in BEAUTi file
if filetype == 'beauti':
    process_beauti(filename)


