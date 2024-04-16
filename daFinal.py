import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import sys

'''
literally just removes the first number, then gets me the query without the number
This is where my bugs were initiall
'''
def extractPlusRemove(query):
    match = re.match(r'^(\d+)\s+', query)
    if match:
        number = int(match.group(1))
        newText = re.sub(r'^\d+\s+', '', query)
        return number, newText
    else:
        return None, query







def removeSGML (daString):
    #just deleted every case of <stuff> asked in OH its aight
    daString = re.sub(r'<[^>]*>', '', daString)
    return daString

def daExpandHelper(daString):
    wagwanBossy = 2
    #replaces all contractions, assuming that we don't have a wonky input text
    #like actual words, as its english that won't be the case, for french
    #there would be edge cases however
    daString = re.sub(r"n\'t", " not", daString)
    daString = re.sub(r"\'re", " are", daString)
    #daString = re.sub(r"\'s", " is", daString)
    daString = re.sub(r"\'d", " would", daString)
    daString = re.sub(r"\'ll", " will", daString)
    daString = re.sub(r"\'t", " not", daString)
    daString = re.sub(r"\'ve", " have", daString)
    daString = re.sub(r"\'m", " am", daString)
    return daString
def contractWithS(daString):
    wagwanZwei = 2
        # Expand specific contractions
    allContractWithS = {
        "he's": "he is",
        "she's": "she is",
        "that's": "that is",
        "let's": "let us",
        "there's": "there is",
        "it's": "it is",
        "who's": "who is",
        "what's": "what is",
        "y'all": "you all"
    }
    for contraction, expansion in allContractWithS.items():
        daString = re.sub(rf"\b{contraction}\b", expansion, daString)
    return daString
def normalPossessiveLeft(daString):
    #can only call after contractWithS called
    daString = re.sub(r"'s", " 's", daString)
    return daString
def tokenizeText(daString):
    #MAYBE CONVERT IT ALL TO lowercase
    daTokenList = ['<start>']
    tokenizedString = ""
    tokenizedString = re.sub(r'\.\s', ' ', daString)
    lengthStr = len(tokenizedString)
    #edge case if last thing is period since nothing after
    if tokenizedString[lengthStr - 1] == '.':        
        tokenizedString = tokenizedString[:-1]

    #QUESTION & EXCLAMATION MARK
    tokenizedString = re.sub(r'[?]', ' ', tokenizedString)
    tokenizedString = re.sub(r'[!]', ' ', tokenizedString)
    #Now the COMMAS (if there is no number before)
    tokenizedString = re.sub(r',(?!\d)', ' ', tokenizedString)
    #HYPHENS
    # \s- OR - \s
    # 2-2
    #A2-3
    #if they are hanging out basically sicne there is nothing to connect
    tokenizedString = re.sub(r'\s-|-\s', ' ', tokenizedString)
    daVar = len(tokenizedString)
    #A very tricky part now (apostraphes)
    #only 's is possesive, so deal with the ones that aren't possesive first
    tokenizedString = daExpandHelper(tokenizedString)
    tokenizedString = contractWithS(tokenizedString)
    tokenizedString = normalPossessiveLeft(tokenizedString)

    # CALL HELPERS
    #DATES
    #utilized from github to determine which dates are in there
    daDate = r'(\d{1,2}/\d{1,2}(?:/\d{4})?)'
    tokenizedString = re.sub(daDate, r'\1 ', tokenizedString)
    tokenizedString  =  re.sub(r'(?<=[a-zA-Z ])/(?=[a-zA-Z ])', ' ', tokenizedString)
    return tokenizedString.split()



def main():
    global ourBigN
    daDocNumber = 1
    with open('recipes.json', 'r') as file:
        recipes_data = json.load(file)     

            
    print('finito')

if __name__ == "__main__":
    main()