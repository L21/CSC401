#!/usr/bin/python
# coding=utf-8
import NLPlib
import re
import sys

"""
helper function -- open word list
file and read content into a list.
"""


def readWordList(path):
    try:
        file = open(path, 'r')
    except IOError:
        print 'cannot open', path + ", please make sure file exists and not corrupted."
        sys.exit(1)
    wordlist = [line.strip().lower() for line in file]
    return wordlist

"""
maleFirstNames = readWordList('maleFirstNames.txt')
abbrevs = readWordList('abbrev.english')
femaleFirstNames = readWordList('femaleFirstNames.txt')
lastNames = readWordList('lastNames.txt')
pnAbbrevs = readWordList('pn_abbrev.english')
"""

maleFirstNames = readWordList('/u/cs401/Wordlists/maleFirstNames.txt')
abbrevs = readWordList('/u/cs401/Wordlists/abbrev.english')
femaleFirstNames = readWordList('/u/cs401/Wordlists/femaleFirstNames.txt')
lastNames = readWordList('/u/cs401/Wordlists/lastNames.txt')
pnAbbrevs = readWordList('/u/cs401/Wordlists/pn_abbrev.english')


months = ['jan.', 'feb.', 'mar.', 'apr.', 'jun.', 'jul.', 'aug.', 'sep.', 'oct.', 'nov.', 'dec.']

"""
helper function - return list of tuples of 
numeric classes and raw tweet texts
"""


def openCSVFile(filePath, GID):
    try:
        file = open(filePath, 'r')
    except IOError:
        print 'cannot open', filePath + ", please make sure file exists and not corrupted."
        sys.exit(1)
    tweetTextList = []
    for i, line in enumerate(file):
        if (int(GID) * 5500 <= i and (int(GID) + 1) * 5500 >= i + 1) or (
                            800000 + (int(GID) * 5500) <= i and 800000 + ((int(GID) + 1) * 5500) >= i + 1):
            numericClass = "<A=" + line[1] + ">"
            line = line.split("\",\"")[5]
            # remove trailing quote
            line = re.sub('"$', '', line)
            tweetTextList.append((numericClass, line))
    file.close()
    return tweetTextList


"""
helper function - replace HTML character to ASCII equivalents
"""


def convertToAscII(inputString):
    # table of html characters
    htmlCharacterCodes = (
        (" ", '&#32;'),
        ('!', '&#33;'),
        ('"', '&#34;'),
        ('#', '&#35;'),
        ('$', '&#36;'),
        ('%', '&#37;'),
        ('&', '&#38;'),
        ('\'', '&#39;'),
        ('(', '&#40;'),
        (')', '&#41;'),
        ('*', '&#42;'),
        ("+", '&#43;'),
        (',', '&#44;'),
        ('-', '&#45;'),
        ('.', '&#46;'),
        ('/', '&#47;'),
        (':', '&#58;'),
        (';', '&#59;'),
        ('<', '&#60;'),
        ('=', '&#61;'),
        ('>', '&#62;'),
        ("?", '&#63;'),
        ('@', '&#64;'),
        ('[', '&#91;'),
        ('\\', '&#92;'),
        (']', '&#93;'),
        ("^", '&#94;'),
        ('_', '&#95;'),
        ('`', '&#96;'),
        ('{', '&#123;'),
        ('|', '&#124;'),
        ('}', '&#125;'),
        ('~', '&#126;'),
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;')
    )
    for htmlCharacterCode in htmlCharacterCodes:
        inputString = inputString.replace(htmlCharacterCode[1], htmlCharacterCode[0])
    return inputString


"""
return a new list of tokens with punctuations 
separated from the tokens. 
"""


def separatePunctuations(tweetTokenList):
    newTokenList = []
    for token in tweetTokenList:
        # separate clitics
        indecies = [index.start() for index in re.finditer(r'\'(m|re|s|ve|ll|d|o)', token)]
        while len(indecies) != 0:
            token = token[:indecies[-1]] + " " + token[indecies[-1]:]
            indecies.pop()
        indecies = [index.start() for index in re.finditer(r'n\'t', token.lower())]
        while len(indecies) != 0:
            token = token[:indecies[-1]] + " " + token[indecies[-1]:]
            indecies.pop()
        # separate punctuations immediately after a character
        indecies = [index.start() for index in re.finditer(r'[a-zA-z][,\[\]\?!;:\-"\/&$£><\+)(\‘\“\’\”]', token)]
        while len(indecies) != 0:
            token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
            indecies.pop()
        # separate punctuations immediately before a character
        indecies = [index.start() for index in re.finditer(r'[\[\],?!;:\-"/&$£><‘“’”\+)(][a-zA-Z0-9]', token)]
        while len(indecies) != 0:
            token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
            indecies.pop()
        # separate single quotes if not part of a clitic
        indecies = [index.start() for index in re.finditer(r'[a-mo-z]\'', token.lower())]
        while len(indecies) != 0:
            token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
            indecies.pop()
        indecies = [index.start() for index in re.finditer(r'^\'\w', token.lower())]
        while len(indecies) != 0:
            token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
            indecies.pop()
        # separate periods that are not part of a abbreviation
        if not ((token.lower() in abbrevs) or (token.lower() in pnAbbrevs)):
            indecies = [index.start() for index in re.finditer(r'[a-zA-z]\.', token)]
            while len(indecies) != 0:
                token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
                indecies.pop()
            indecies = [index.start() for index in re.finditer(r'\.[a-zA-z]', token)]
            while len(indecies) != 0:
                token = token[:indecies[-1] + 1] + " " + token[indecies[-1] + 1:]
                indecies.pop()
        newTokens = token.split()
        for newToken in newTokens:
            newTokenList.append(newToken)
    return newTokenList


"""
helper function -- take a raw tweet text and 
return a list of lists of tokens for each sentence
(e.g. [[token1OfSentence1,...,tokenNOfSentence1], [token1OfSentence2,...,tokenNOfSentence2]...]) 
"""


def separateSentencesAndPunctuations(tweetText):
    lineList = []
    line = []
    # get all the tokens
    tokens = tweetText.strip().split()
    # last token must be a sentence end
    for index in range(len(tokens)):
        if index < len(tokens) - 1 and isSentenceEnd(tokens[index], tokens[index + 1]):
            line.append(tokens[index])
            lineList.append(line)
            line = []
        else:
            line.append(tokens[index])
    if len(line) > 0:
        lineList.append(line)

    # separate punctuations for each line
    result = []
    for line in lineList:
        result.append(separatePunctuations(line))
    return result


"""
helper function -- retunr true if the given 
token is the end of a sentence. 
"""


def isSentenceEnd(token, nextToken):
    # ends with '.'
    if token[-1] == '.':
        if (token.lower() == 'st.'):
            if (nextToken.lower() in (lastNames + femaleFirstNames + maleFirstNames)):
                return False
            elif re.match(r'^[a-z0-9]', nextToken):
                return False
            else:
                return True
        # cases not likely to be a sentence end
        elif (token.lower() in pnAbbrevs):
            return False
        elif (token.lower() in months):
            if re.match(r'^[0-9]', nextToken):
                return False
            else:
                return True
        elif (token.lower() in abbrevs):
            if (re.match(r'[A-Z0-9]', nextToken)):
                return True
            else:
                return False
        elif (re.match(r'\W', nextToken)):
            return False
        else:
            return True
    # ends with a quotation mark
    elif re.match(r'[\'\"]$', token[-1]):
        if re.match(r'[\?\.\!\:\;\)][\'\")]$', token):
            return True
        else:
            return False
    # ends with ?,:,; or !
    elif re.match(r'[\!\;\?]$', token[-1]):
        return True
    # ends with other punctuations or no punctuation
    else:
        return False


"""
helper function - pre-process and tokenize 
tuple of numeric class and raw tweet text.
"""


def tokenize(tweetTextTuple):
    tweetText = tweetTextTuple[1]
    # remove HTML tags and attributes
    tweetText = re.sub(r'<[^>]+>', '', tweetText)
    # replace HTML codes with ASCII
    tweetText = convertToAscII(tweetText)
    # remove http://* URL
    tweetText = re.sub('http://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', tweetText)
    # remove www.* URL
    tweetText = re.sub('www.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', tweetText)
    # remove "@" and "#"
    tweetText = re.sub(r'[#@]', ' ', tweetText)
    # tokenize, split sentences and separate punctuations
    tweetTokens = separateSentencesAndPunctuations(tweetText)
    return tweetTokens


# main function
if __name__ == '__main__':
    if len(sys.argv) == 3:
        inputFilePath = sys.argv[1]
        # try to open the specified input file
        tweetTextList = openCSVFile(inputFilePath,0)
        # try to create output file
        try:
            outputFile = open(sys.argv[2], 'w')
        except IOError:
            print "cannot create", sys.argv[2] + ", please try again with a different filename/path"
            sys.exit(1)
    elif len(sys.argv) == 4:
        inputFilePath = sys.argv[1]
        # try to open the specified input file
        tweetTextList = openCSVFile(inputFilePath, sys.argv[2])
        # try to create output file
        try:
            outputFile = open(sys.argv[3], 'w')
        except IOError:
            print "cannot create", sys.argv[3] + ", please try again with a different filename/path"
            sys.exit(1)
    else:
        print "twtt.py <input_filename> <group_number> <output_filename>"
        sys.exit(1);
    # pre-process and tokenize each tuple
    postProcessList = []
    tagger = NLPlib.NLPlib()
    for tweetTextTuple in tweetTextList:
        tweetTokensTuple = (tweetTextTuple[0], tokenize(tweetTextTuple))
        postProcessList.append(tweetTokensTuple)

    # tag all tokens
    for tweetTokensTuple in postProcessList:
        outputFile.write(tweetTokensTuple[0] + "\n")
        for tokens in tweetTokensTuple[1]:
            tags = tagger.tag(tokens)
            line = ' '.join(['/'.join([w, t]) for w, t in zip(tokens, tags)]) + "\n"
            # write to file
            outputFile.write(line)
    outputFile.close()    
