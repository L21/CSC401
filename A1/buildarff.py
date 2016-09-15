#!/usr/bin/python
# coding=utf-8
import re
import sys
import time

"""
helper function -- open word list
file and read content into a list.
"""
def read_word_list(path):
    try:
        file = open(path, 'r')
    except IOError:
        print 'cannot open', path + ", please make sure file exists and not corrupted."
        sys.exit(1)
    wordlist = [line.strip() for line in file]
    wordlist = filter(None, wordlist)
    file.close()
    return wordlist


"""
helper function -- return number of total
occurrences of given word list in the tweet
sentences.
"""
def count_word_occurrence(words, sentences):
    count = 0
    words_str = '|'.join(words)
    for sentence in sentences:
        matches = re.findall(r'(\W|^)\(' + words_str.lower() + r'\)/', sentence.lower())
        count += len(matches)
    return count


"""
helper function -- return number of occurrences
of given list of tags in the tweet sentences.
"""
def count_tag_occurrence(tags, sentences):
    count = 0
    tags_str = ' |'.join(tags)
    for sentence in sentences:
        matches = re.findall(r'/' + tags_str, sentence)
        count += len(matches)
    return count

"""
helper function -- append number of matches
of given regular expression in the tweet sentences
into data list.
"""
def count_regex_occurrence(regex, sentences):
    count = 0
    for sentence in sentences:
        matches = re.findall(regex, sentence)
        count += len(matches)
    return count

def count_muiltple_parts_occurrence(regex, sentences):
    count = 0
    for sentence in sentences:
        count += len(re.findall(regex, sentence))
    return count

"""
helper function -- return average length of
elements (that match the regular expression,
regex) in a list. Calculate
average length of all elements if restriction
is empty string.
"""
def average_length(item_list, regex):
    if len(item_list) == 0:
        print "ERROR: cannot calculate average on empty list"
        sys.exit(1)
    elif regex == '':
        avrg = float(sum(len(item) for item in item_list)) / float(len(item_list))
        return avrg
    else:
        item_sum = 0
        length_sum = 0
        for item in item_list:
            if not (re.match(regex, item)):
                length_sum += len(item)
                item_sum += 1
        if item_sum == 0:
            return 0
        avrg = float(length_sum) / float(item_sum)
        return avrg

if __name__ == '__main__':
    # set-up global variables
    FIRST_PERSON = read_word_list('First-person')
    SECOND_PERSON = read_word_list('Second-person')
    THIRD_PERSON = read_word_list('Third-person')
    SLANG = read_word_list('Slang')
    #CONJUNCT = read_word_list('Conjunct')
    POSSIBLE_PUNC_PATTERN = r'#$.,:()"‘“’”'
    FEATURES = ["First person pronouns", "Second person pronouns", "Third person pronouns",
                "Coordinating conjunctions", "Past-tense verbs", "Future-tense verbs", "Commas",
                "Colons, and semi-colons", "Dashes", "Parentheses", "Ellipses", "Common nouns", "Proper nuons",
                "Adverbs", "wh-words", "Modern slang acronyms",
                "Words all in upper case (at lease 2 letters long)", "Average lengths of sentences (in tokens)",
                "Average length of tokens, excluding punctuation tokens (in characters)",
                "Number of sentences"]
    PAST_TENSE = ["VBD"]
    FUTURE_TENSE = ['\'ll', 'will', 'gonna']
    COMMON_NOUNS = ['NN', 'NNS']
    PROPER_NOUNS = ['NNP', 'NNPS']
    ADVERBS = ['RB', 'RBR', 'RBS']
    WH_WORDS = ['WDT', 'WP', 'WP$', 'WRB']
    CONJUNCT = ['and', 'but', 'for', 'nor', 'or', 'so', 'yet']

    # if number of data points is given

    if len(sys.argv) == 4 and re.match(r'^[0-9]+', sys.argv[3]):
        # record the max data points number for each class
        maxDataPoint = int(sys.argv[3])
    # if no data points number is given
    elif len(sys.argv) == 3:
        # try to open the specified input file
        maxDataPoint = -1
    else:
        print "USAGE: buildarff.py <input_filename> <output_filename> [max_data_point_number]"
        sys.exit(1)

    tweets = read_word_list(sys.argv[1])
    # try to create output file
    try:
        outputFile = open(sys.argv[2], 'w')
    except IOError:
        print "cannot create", sys.argv[2] + ", please try again with a different filename/path"
        sys.exit(1)

    outputFile.write("@relation tweets\n")
    # write attributes into output file
    for feature in FEATURES:
        line = "@attribute \"" + feature + "\" numeric\n"
        outputFile.write(line)
    outputFile.write("@attribute class {0,4}")
    # write header "@data" into output file
    outputFile.write("\n@data\n")
    # gather information for each tweet text
    current_tweet = []
    classNum = 0
    prevClassNUm = 0
    # dictionary for classes and number of occurrences
    classes = {}
    begin = time.time()
    for line in tweets:
        # beginning of the a new tweet
        if re.match(r'^<A=', line):
            classNum = int(line.strip()[-2])
            if not classNum in classes:
                classes[classNum] = 0
            # process previous tweet
            if len(current_tweet) != 0 and (maxDataPoint == -1 or classes[prevClassNum] < maxDataPoint):
                classes[classNum] += 1
                numeric_data = ''
                # counts of first person pronouns
                numeric_data += str(count_word_occurrence(FIRST_PERSON, current_tweet)) + ','
                # counts of second person pronouns
                numeric_data += str(count_word_occurrence(SECOND_PERSON, current_tweet)) + ','
                # counts of third person pronouns
                numeric_data += str(count_word_occurrence(THIRD_PERSON, current_tweet)) + ','
                # counts of coordinating conjunctions
                numeric_data += str(count_word_occurrence(CONJUNCT, current_tweet)) + ','
                # counts of past-tense verbs
                numeric_data += str(count_tag_occurrence(PAST_TENSE, current_tweet)) + ','
                # counts of future-tense verbs
                count = count_word_occurrence(FUTURE_TENSE, current_tweet)
                count += count_muiltple_parts_occurrence(r'[Gg]oing/\w+ to/\w+ \w+/VB', current_tweet)
                numeric_data += str(count) + ','
                # counts of commas
                numeric_data += str(count_regex_occurrence(r',/,', current_tweet)) + ','
                # counts of colons and semi-colons
                numeric_data += str(count_regex_occurrence(r'[:;]/:', current_tweet)) + ','
                # counts of dashes
                numeric_data += str(count_regex_occurrence(r'—+/', current_tweet)) + ','
                # counts of parentheses
                numeric_data += str(count_regex_occurrence(r'[\(\)\{\}\<\>\[\]]', current_tweet)) + ','
                # counts of ellipses
                numeric_data += str(count_regex_occurrence(r'[ \w]..+[\w $]', current_tweet)) + ','
                # counts of common nouns
                numeric_data += str(count_tag_occurrence(COMMON_NOUNS, current_tweet)) + ','
                # counts of proper nouns
                numeric_data += str(count_tag_occurrence(PROPER_NOUNS, current_tweet)) + ','
                # counts of adverbs
                numeric_data += str(count_tag_occurrence(ADVERBS, current_tweet)) + ','
                # counts of wh-words
                numeric_data += str(count_tag_occurrence(WH_WORDS, current_tweet)) + ','
                # counts of modern slang acronyms
                numeric_data += str(count_word_occurrence(SLANG, current_tweet)) + ','
                # counts of words all in upper case (at least 2 letters long)
                numeric_data += str(count_regex_occurrence(r'[A-Z][A-Z]+/', current_tweet)) + ','
                # average length of sentences in tokens
                tokens = []
                for sentence in current_tweet:
                    tokens += sentence.split()
                numeric_data += str(average_length(tokens, r'^\w+$')) + ','
                
                sentences = []
                for sentence in current_tweet:
                    sentences.append(sentence.split())
                numeric_data += str(average_length(sentences, '')) + ','
                # average length of tokens, excluding
                numeric_data += str(len(current_tweet)) + ','
                # numeric class of the tweet
                numeric_data += str(prevClassNum) + '\n'
                # write to output file
                outputFile.write(numeric_data)
            
            # clear current tweet data
            current_tweet = []
        
        # a tweet sentence
        else:
            prevClassNum = classNum
            current_tweet.append(line)

    # handle last tweet text
    if len(current_tweet) != 0 and (maxDataPoint == -1 or classes[prevClassNum] < maxDataPoint):
            numeric_data = ''
            # counts of first person pronouns
            numeric_data += str(count_word_occurrence(FIRST_PERSON, current_tweet)) + ','
            # counts of second person pronouns
            numeric_data += str(count_word_occurrence(SECOND_PERSON, current_tweet)) + ','
            # counts of third person pronouns
            numeric_data += str(count_word_occurrence(THIRD_PERSON, current_tweet)) + ','
            # counts of coordinating conjunctions
            numeric_data += str(count_word_occurrence(CONJUNCT, current_tweet)) + ','
            # counts of past-tense verbs
            numeric_data += str(count_tag_occurrence(PAST_TENSE, current_tweet)) + ','
            # counts of future-tense verbs
            count = count_word_occurrence(FUTURE_TENSE, current_tweet)
            count += count_muiltple_parts_occurrence(r'[Gg]oing/\w+ to/\w+ \w+/VB', current_tweet)
            numeric_data += str(count) + ','
            # counts of commas
            numeric_data += str(count_regex_occurrence(r',/,', current_tweet)) + ','
            # counts of colons and semi-colons
            numeric_data += str(count_regex_occurrence(r'[:;]/:', current_tweet)) + ','
            # counts of dashes
            numeric_data += str(count_regex_occurrence(r'—+/', current_tweet)) + ','
            # counts of parentheses
            numeric_data += str(count_regex_occurrence(r'[\(\)\{\}\<\>\[\]]', current_tweet)) + ','
            # counts of ellipses
            numeric_data += str(count_regex_occurrence(r'[ \w]..+[\w $]', current_tweet)) + ','
            # counts of common nouns
            numeric_data += str(count_tag_occurrence(COMMON_NOUNS, current_tweet)) + ','
            # counts of proper nouns
            numeric_data += str(count_tag_occurrence(PROPER_NOUNS, current_tweet)) + ','
            # counts of adverbs
            numeric_data += str(count_tag_occurrence(ADVERBS, current_tweet)) + ','
            # counts of wh-words
            numeric_data += str(count_tag_occurrence(WH_WORDS, current_tweet)) + ','
            # counts of modern slang acronyms
            numeric_data += str(count_word_occurrence(SLANG, current_tweet)) + ','
            # counts of words all in upper case (at least 2 letters long)
            numeric_data += str(count_regex_occurrence(r'[A-Z][A-Z]+/', current_tweet)) + ','
            # average length of sentences in tokens
            tokens = []
            for sentence in current_tweet:
                tokens += sentence.split()
            numeric_data += str(average_length(tokens, r'^\w+$')) + ','
            
            sentences = []
            for sentence in current_tweet:
                sentences.append(sentence.split())
            numeric_data += str(average_length(sentences, '')) + ','
            # average length of tokens, excluding
            numeric_data += str(len(current_tweet)) + ','
            # numeric class of the tweet
            numeric_data += str(prevClassNum) + '\n'
            # write to output file
            outputFile.write(numeric_data)
            current_tweet = []

    outputFile.close()

