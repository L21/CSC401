# -*- coding: utf-8 -*-
# ibmTrain.py
# 
# This file produces 11 classifiers using the NLClassifier IBM Service
# 
# TODO: You must fill out all of the functions in this file following 
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#

###IMPORTS###################################
#TODO: add necessary imports

import urllib2
import sys
import requests
import re
import codecs
requests.packages.urllib3.disable_warnings()

###HELPER FUNCTIONS##########################

def convert_training_csv_to_watson_csv_format(input_csv_name, group_id, output_csv_name): 
	# Converts an existing training csv file. The output file should
	# contain only the 11,000 lines of your group's specific training set.
	#
	# Inputs:
	#	input_csv - a string containing the name of the original csv file
	#		ex. "my_file.csv"
	#
	#	output_csv - a string containing the name of the output csv file
	#		ex. "my_output_file.csv"
	#
	# Returns:
	#	None
	
	#TODO: Fill in this function
	try:
		input_file = codecs.open(input_csv_name, 'r', errors='ignore', encoding= 'utf-8')

	except IOError:
		print 'cannot open', input_csv_name + ", please make sure file exists and not corrupted."
		sys.exit(1)
	try: 
		output_file = codecs.open(output_csv_name, 'w', encoding= 'utf-8')
	except IOError:
		print 'cannot create', output_csv_name + ", please make sure file exists and not corrupted."
		sys.exit(1)

	tweetTextList = []

	for i, line in enumerate(input_file):
		if (int(group_id) * 5500 <= i and (int(group_id) + 1) * 5500 >= i + 1) or (
                            800000 + (int(group_id) * 5500) <= i and 800000 + ((int(group_id) + 1) * 5500) >= i + 1):
			parts = line.split("\",\"")
			line = '"' + re.sub('[\n"]', '', parts[5]) + '",' + line[1] + '\n'
            # remove all double quotes
			output_file.write(line)
	input_file.close()
	output_file.close()
	return
	
def extract_subset_from_csv_file(input_csv_file, n_lines_to_extract, output_file_prefix='ibmTrain'):
	# Extracts n_lines_to_extract lines from a given csv file and writes them to 
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs: 
	#	input_csv - a string containing the name of the original csv file from which
	#		a subset of lines will be extracted
	#		ex. "my_file.csv"
	#	
	#	n_lines_to_extract - the number of lines to extract from the csv_file, as an integer
	#		ex. 500
	#
	#	output_file_prefix - a prefix for the output csv file. If unspecified, output files 
	#		are named 'ibmTrain#.csv', where # is the input parameter n_lines_to_extract.
	#		The csv must be in the "watson" 2-column format.
	#		
	# Returns:
	#	None
	
	#TODO: Fill in this function
	try:
		input_file = codecs.open(input_csv_file, 'r', errors='ignore', encoding= 'utf-8')
	except IOError:
		print 'cannot open', input_csv_file + ", please make sure file exists and not corrupted."
		sys.exit(1)
	try:
		output_file = codecs.open(output_file_prefix+str(n_lines_to_extract) + '.csv', 'w', errors='ignore', encoding='utf-8')
	except IOError:
		print 'cannot create', output_file_prefix+str(n_lines_to_extract) + '.csv' + ", please make sure file exists and not corrupted."
		sys.exit(1)
	tweetTextList = []

	classes = {0:0, 4:0}
	for line in input_file:
		if (line[-2] == '0' and classes[0] < n_lines_to_extract):
			classes[0] += 1
			# parts = line.split("\",\"")
			# line = '"' + re.sub('[\n"“”]', '', parts[5]) + '",' + line[1] + '\n'
			output_file.write(line)
		elif (line[-2] == '4' and classes[4] < n_lines_to_extract):
			classes[4] += 1
			# parts = line.split("\",\"")
			output_file.write(line)
	input_file.close()
	output_file.close()
	return
	
def create_classifier(username, password, n, input_file_prefix='ibmTrain'):
	#TODO: Fill in this function
	# Creates a classifier using the NLClassifier service specified with username and password.
	# Training_data for the classifier provided using an existing csv file named
	# ibmTrain#.csv, where # is the input parameter n.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	n - identification number for the input_file, as an integer
	#		ex. 500
	#
	#	input_file_prefix - a prefix for the input csv file, as a string.
	#		If unspecified data will be collected from an existing csv file 
	#		named 'ibmTrain#.csv', where # is the input parameter n.
	#		The csv must be in the "watson" 2-column format.
	#
	# Returns:
	# 	A dictionary containing the response code of the classifier call, will all the fields 
	#	specified at
	#	http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/natural-language-classifier/api/v1/?curl#create_classifier
	#   
	#
	# Error Handling:
	#	This function should throw an exception if the create classifier call fails for any reason
	#	or if the input csv file does not exist or cannot be read.
	#
	
	#TODO: Fill in this function
	filename = input_file_prefix+str(n)+'.csv'

	#headers = {'Content-type': 'application/json'}

	payload = {'training_metadata':"{\"language\":\"en\",\"name\":\"TutorialClassifier\"}"}

	files = {'training_data': open(filename, 'r')}
	try:	
		print "Sending training data to Watson......\n"
		r = requests.post(url='https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/', auth=(username, password), files=files, data=payload)
	except:
		print "Encountered an error when creating the classifier, exiting......\n"
		sys.exit(1)
	return r.json()

if __name__ == "__main__":
	
	### STEP 1: Convert csv file into two-field watson format
	input_csv_name = '/u/cs401/A1/tweets/training.1600000.processed.noemoticon.csv'

	#DO NOT CHANGE THE NAME OF THIS FILE
	output_csv_name = 'training_11000_watson_style.csv'
	print "Converting training file......\n"
	convert_training_csv_to_watson_csv_format(input_csv_name, 56, output_csv_name)
	
	
	### STEP 2: Save 11 subsets in the new format into ibmTrain#.csv files
	#TODO: extract all 11 subsets and write the 11 new ibmTrain#.csv files
	#
	# you should make use of the following function call:
	#
	# n_lines_to_extract = 500
	# extract_subset_from_csv_file(input_csv,n_lines_to_extract)
	subset_sizes = [500, 2500, 5000]
	print "Extracting subsets from training file.....\n"
	for size in subset_sizes:
 		extract_subset_from_csv_file(output_csv_name, size)

	### STEP 3: Create the classifiers using Watson
	
	#TODO: Create all 11 classifiers using the csv files of the subsets produced in 
	# STEP 2
	# 
	#
	# you should make use of the following function call
	# n = 500
	# username = '<ADD USERNAME>'
	# password = '<ADD PASSWORD>'
	# create_classifier(username, password, n, input_file_prefix='ibmTrain')
	username = "a87b279f-a3ea-4673-b13a-b8c1bdc329a7"
	password = "d028T11KGQqJ"
	for size in subset_sizes:
		print create_classifier(username, password, size, input_file_prefix='ibmTrain')
