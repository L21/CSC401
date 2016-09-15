# ibmTest.py
# This file tests all 11 classifiers using the NLClassifier IBM Service
# previously created using ibmTrain.py
# 
# TODO: You must fill out all of the functions in this file following 
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#		You may also find it helpful to reuse some of your functions from ibmTrain.py.
#
import sys
import requests
requests.packages.urllib3.disable_warnings()
def get_classifier_ids(username,password):
	# Retrieves a list of classifier ids from a NLClassifier service 
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#		
	# Returns:
	#	a list of classifier ids as strings
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason
	#
	
	#TODO: Fill in this function
	try:
		r = requests.get(url='https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/', auth=(username, password))
	except:
		print "Encountered an error when getting the classifier, exiting......\n"
		sys.exit(1)
	result = r.json()
	classifier_id_list = []
	for classifier in result['classifiers']:
		classifier_id_list.append(classifier['classifier_id'])
	return classifier_id_list

def assert_all_classifiers_are_available(username, password, classifier_id_list):
	# Asserts all classifiers in the classifier_id_list are 'Available' 
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id_list - a list of classifier ids as strings
	#		
	# Returns:
	#	None
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason AND 
	#	It should throw an error if any classifier is NOT 'Available'
	#
	
	#TODO: Fill in this function
	for classifier_id in classifier_id_list:
		try:
			r = requests.get(url='https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/' + classifier_id, auth=(username, password))
		except:
			print "Encountered an error when getting the classifier detail, exiting......\n"
			sys.exit(1)
		if "Available" not in r.json()['status']:
			print "ERROR: classifier " + classifier_id + "is not in available state, please check back later.\n"
			print "exiting .......\n"
			sys.exit(2)
	return

def classify_single_text(username,password,classifier_id,text):
	# Classifies a given text using a single classifier from an NLClassifier 
	# service
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id - a classifier id, as a string
	#		
	#	text - a string of text to be classified, not UTF-8 encoded
	#		ex. "Oh, look a tweet!"
	#
	# Returns:
	#	A "classification". Aka: 
	#	a dictionary containing the top_class and the confidences of all the possible classes 
	#	Format example:
	#		{'top_class': 'class_name',
	#		 'classes': [
	#					  {'class_name': 'myclass', 'confidence': 0.999} ,
	#					  {'class_name': 'myclass2', 'confidence': 0.001}
	#					]
	#		}
	#
	# Error Handling:
	#	This function should throw an exception if the classify call fails for any reason 
	#
	
	#TODO: Fill in this function
	payload = {'text':text}
	try:
		r = requests.get(url='https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'
		 + classifier_id + '/classify', auth=(username, password), params=payload)
	except:
		print "Encountered an error when getting the classifier detail, exiting......\n"
		sys.exit(1)
	result = r.json()
	class_dict = {'top_class':result['top_class'],'classes':result['classes']}
	return class_dict

def classify_all_texts(username,password,input_csv_name):
    # Classifies all texts in an input csv file using all classifiers for a given NLClassifier
    # service.
    #
    # Inputs:
    #       username - username for the NLClassifier to be used, as a string
    #
    #       password - password for the NLClassifier to be used, as a string
    #      
    #       input_csv_name - full path and name of an input csv file in the 
    #              6 column format of the input test/training files
    #
    # Returns:
    #       A dictionary of lists of "classifications".
    #       Each dictionary key is the name of a classifier.
    #       Each dictionary value is a list of "classifications" where a
    #       "classification" is in the same format as returned by
    #       classify_single_text.
    #       Each element in the main dictionary is:
    #       A list of dictionaries, one for each text, in order of lines in the
    #       input file. Each element is a dictionary containing the top_class
    #       and the confidences of all the possible classes (ie the same
    #       format as returned by classify_single_text)
    #       Format example:
    #              {'classifiername':
    #                      [
    #                              {'top_class': 'class_name',
    #                              'classes': [
    #                                        {'class_name': 'myclass', 'confidence': 0.999} ,
    #                                         {'class_name': 'myclass2', 'confidence': 0.001}
    #                                          ]
    #                              },
    #                              {'top_class': 'class_name',
    #                              ...
    #                              }
    #                      ]
    #              , 'classifiername2':
    #                      [
    #                      ...      
    #                      ]
    #              ...
    #              }
    #
    # Error Handling:
    #       This function should throw an exception if the classify call fails for any reason
    #       or if the input csv file is of an improper format.
    #
    #TODO: Fill in this function
	result = {}
	classifier_id_list = get_classifier_ids(username,password)
	assert_all_classifiers_are_available(username, password, classifier_id_list)
	for i in classifier_id_list:
		result[i] = []
	try:
		input_file = open(input_csv_name, 'r')
	except IOError:
		print 'cannot open', input_csv_name + ", please make sure file exists and not corrupted."
		sys.exit(1)
	for line in input_file:
		components = line.split('","')
		if len(components) != 6:
			print "ERROR: invalid format of input file.\n"
			sys.exit(2)
		else:
			# trim trailing double qoute and new line character
			text = components[5].replace('"\n', '')
			for i in classifier_id_list:
				result[i].append(classify_single_text(username, password, i, text))
	return result

# helper function -- check if current text is being classified correctly 
# classifer_tuple = (true_class, classifier_result)
def compare_classification(classifier_tuple):
	classified = int(classifier_tuple[1]['top_class'])
	if classifier_tuple[0] == classified:
		return 1
	else:
		return 0

# helper function -- extract class numbers from a line of input csv file
def take_class(line):
	components = line.split('","')
	if len(components) != 6:
		print "ERROR: invalid format of input file.\n"
		sys.exit(2)
	else:
		# trim trailing double qoute and new line character
		class_num = components[0][1]
	return int(class_num)

def compute_accuracy_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the accuracy of this
	# classifier according to the input csv file
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the 
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text) 	
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the  
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The accuracy of the classifier, as a fraction between [0.0-1.0] (ie percentage/100). \
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the 
	#	inputs.
	#
	
	#TODO: fill in this function
	try:
		input_file = open(input_csv_file_name, 'r')
	except IOError:
		print 'cannot open', input_csv_file_name + ", please make sure file exists and not corrupted."
		sys.exit(1)
	class_nums = map(take_class, input_file.readlines())
	classifier_tuple = zip(class_nums, classifier_dict)
	hit_list = map(compare_classification, classifier_tuple)
	return reduce(lambda x, y: x + y, hit_list) / float(len(hit_list))


def compute_average_confidence_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the average 
	# confidence of this classifier wrt the selected class, according to the input
	# csv file. 
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the 
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text) 	
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the  
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The average confidence of the classifier, as a number between [0.0-1.0]
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the 
	#	inputs.
	
	#TODO: fill in this 
	try:
		input_file = open(input_csv_file_name, 'r')
	except IOError:
		print 'cannot open', input_csv_file_name + ", please make sure file exists and not corrupted."
		sys.exit(1)
	class_nums = map(take_class, input_file.readlines())
	classifier_tuples = zip(class_nums, classifier_dict)
	correct_list = []
	incorrect_list = []
	for classifier_tuple in classifier_tuples:
		if classifier_tuple[0] == int(classifier_tuple[1]['top_class']):
			for i in (classifier_tuple[1]['classes']):
				if i['class_name'] == str(classifier_tuple[0]):
					correct_list.append(i['confidence'])
		else:
			for i in (classifier_tuple[1]['classes']):
				if i['class_name'] != str(classifier_tuple[0]):
					incorrect_list.append(i['confidence'])
	#print correct_list
	#print incorrect_list
	if len(correct_list) == 0:
		average_correct_list = 0
	elif len(correct_list) == 1:
		average_currect_list = correct_list[0]
	else:
		average_correct_list = reduce(lambda x, y: x + y, correct_list) / float(len(correct_list))
	if len(incorrect_list) == 0:
		average_incorrect_list = 0
	elif len(incorrect_list) == 1:
		average_incurrect_list = incorrect_list[0]
	else:
		average_incorrect_list = reduce(lambda x, y: x + y, incorrect_list) / float(len(incorrect_list))

	return (average_correct_list, average_incorrect_list)
	#return 

if __name__ == "__main__":

	#input_test_data = 'test.csv'
	input_test_data = 'testdata.manualSUBSET.2009.06.14.csv'
	username = "a87b279f-a3ea-4673-b13a-b8c1bdc329a7"
	password = "d028T11KGQqJ"

	classifier_ids = get_classifier_ids(username,password)
	#STEP 1: Ensure all 11 classifiers are ready for testing
	print "Checking if all classifiers are available......\n"
	assert_all_classifiers_are_available(username, password, classifier_ids)
	#STEP 2: Test the test data on all classifiers
	print "Classifing all text......\n"
	classified_dict = classify_all_texts(username,password,input_test_data)
	#STEP 3: Compute the accuracy for each classifier
	print "Computing accuracies.......\n"
	accuracies = map(lambda x: compute_accuracy_of_single_classifier(x, input_test_data), classified_dict.values())
	print accuracies
	#STEP 4: Compute the confidence of each class for each classifier
	print "Computing averages.......\n"
	averages = map(lambda x: compute_average_confidence_of_single_classifier(x, input_test_data), classified_dict.values())
	print averages