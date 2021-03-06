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
# File parsing routines have very minimal error checking capabilities,
# definitely no substitute for a comprehensive file format checker
#
# Author: Robert Sinkovits, SDSC
#
# Usage: cipres_data_parse [file_name] <-t file_type>

import re
import argparse

# Process the command line arguments
file_types = ['beast', 'beast2', 'migrate_parm', 'migrate_infile']
parser     = argparse.ArgumentParser(description='Process file name and file type cmd line args')
parser.add_argument(dest='file_name')
parser.add_argument('-t', '--type', dest='file_type', choices=file_types, default='unknown')
args      = parser.parse_args()
file_name = args.file_name
file_type = args.file_type

def process_beast(file_name):

    # Process BEAST files and return following
    #
    #    datatype (nucleotide or amino acid)
    #    codon_partioning (True or False)
    #    nu_partitions (number of partitions)
    #    nu_patterns (number of patterns)

    # Initialize results
    datatype           = 'unknown'
    codon_partitioning = False
    nu_partitions      = 0
    pattern_count      = 0

    # Start by assuming successful parsing of file
    err_code = 0

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
                datatype = re.sub('\s*', '', line)

            # Process the lines that list number of patterns
            # Increment pattern and partition counts
            if cregex_patterns.search(line):
                line = re.sub(regex_patterns, '', line)
                line = re.sub('\D.*', '', line)
                pattern_count += int(line)
                nu_partitions += 1
                    
            # Look for lines that contain the string "codon"
            if cregex_codon.search(line):
                codon_partitioning = True

    # Test for errors:
    # Data type is not set to aminoacid or nucleotide
    if datatype != 'aminoacid' and datatype != 'nucleotide':
        err_code = 1
    # Number of partitions or pattern counts non-positive numbers
    if nu_partitions <= 0 or pattern_count <= 0:
        err_code = 1

    return err_code, datatype, codon_partitioning, nu_partitions, pattern_count

def process_beast2(file_name):

    # Process BEAST2 files and return following
    #
    #    nu_partitions (number of partitions)

    # Partition count is determined from the number of <distribution
    # ...> </distribution> pairs appearing AFTER the tag starting with
    # <distribution id="likelihood"

    # Initialize results
    nu_partitions = 0
    start_counting = False

    # Start by assuming successful parsing of file
    err_code = 0

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.rstrip()
            
            # Look for the starting line
            if line.find('<distribution id="likelihood"') >= 0:
                start_counting = True
                continue
                
            # Start counting partitions
            if start_counting and line.find('<distribution') >= 0 and line.find('/>') < 0:
                nu_partitions += 1

    # Test for errors:
    # Number of partitions non-positive number
    if nu_partitions <= 0:
        err_code = 1

    return err_code, nu_partitions

def process_migrate_parm(file_name):

    # Process Migrate parmfile and return following
    #
    #    num_reps (Number of replicates)

    # Replicate count is determined from the line 
    # replicate=< NO | YES:<VALUE | LastChains> >

    # Initialize replicates to 1
    num_reps = 1

    # Start by assuming successful parsing of file
    err_code = 0

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.rstrip()
            
            # Look for the starting line
            if line.find('replicate=YES') >= 0:
                p1, num_reps = line.split(':')
                break

    # Test for errors:
    # number of replicates is not a valid number
    if not str(num_reps).isdigit():
        err_code = 1

    return err_code, num_reps

def process_migrate_infile(file_name):

    # Process Migrate infile and return following
    #
    #    Number of num_loci

    # Num_Loci count is determined from 1st record, 2nd field

    # Initialize num_loci to 1
    num_loci = 1

    # Start by assuming successful parsing of file
    err_code = 0

    with open(file_name, 'rU') as fin:
        for line in fin:
            line = line.strip()
            pline = line.split()
            num_loci = pline[1]
            break

    # Test for errors:
    # number of loci is not a valid number
    if not str(num_loci).isdigit():
        err_code = 1

    return err_code, num_loci

#--------------------------------------------------------------
# ------------------- Start main program ----------------------
#--------------------------------------------------------------

# Determine the input file type if not already set
if file_type == 'unknown':
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
    err_code, datatype, codon_partitioning, nu_partitions, pattern_count = process_beast(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'err_code=' + str(err_code) + '\n'
    results += 'datatype=' + datatype + '\n'
    results += 'codon_partitioning=' + str(codon_partitioning) + '\n'
    results += 'nu_partitions=' + str(nu_partitions) +'\n'
    results += 'pattern_count=' + str(pattern_count)

# Process BEAST2 files
if file_type == 'beast2':
    err_code, nu_partitions = process_beast2(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'err_code=' + str(err_code) + '\n'
    results += 'nu_partitions=' + str(nu_partitions)

# Process Migrate parmfile
if file_type == 'migrate_parm':
    err_code, num_reps = process_migrate_parm(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'err_code=' + str(err_code) + '\n'
    results += 'num_reps=' + str(num_reps)

# Process Migrate infile
if file_type == 'migrate_infile':
    err_code, num_loci = process_migrate_infile(file_name)
    results =  'file_type=' + file_type + '\n'
    results += 'err_code=' + str(err_code) + '\n'
    results += 'num_loci=' + str(num_loci)

# Unknown or unidentifiable file type
if file_type == 'unknown':
    results =  'file_type=' + file_type + '\n'
    results += 'err_code=1'

print results
