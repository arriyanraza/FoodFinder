import numpy as np
import re
import ast
import pandas as pd
import tensorflow
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences 
from tensorflow.keras.layers import Embedding 
from tensorflow.keras.models import Sequential 


def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def load_data(filename):
    data = pd.read_csv(filename)
    combined_texts = [clean_text(row['title'] + ' ' + ' '.join(ast.literal_eval(row['NER'])))
                      for index, row in data.iterrows()]
    
    # print(combined_texts)
    # breakpoint()

    return combined_texts #, data['title'], data['NER'].apply(ast.literal_eval), data['link']

def load_names(filename):
    data = pd.read_csv(filename)
    combined_texts = [clean_text(row['title'])  for index, row in data.iterrows()]
    recipeList = []
    for index, row in data.iterrows():
        tup = (clean_text(row["title"]), clean_text(row["NER"]), clean_text(row['directions']))
        recipeList.append(tup)

    return recipeList

def cosine_similarity(vec1, vec2):
    # Flatten the matrices into one-dimensional arrays
    vec1_flat = np.ravel(vec1)
    vec2_flat = np.ravel(vec2)
    
    # Compute cosine similarity between the flattened arrays
    dot_product = np.dot(vec1_flat, vec2_flat)
    norm_vec1 = np.linalg.norm(vec1_flat)
    norm_vec2 = np.linalg.norm(vec2_flat)
    
    similarity = dot_product / (norm_vec1 * norm_vec2)
    
    return similarity

def main():
        
    sentences = load_data('full_dataset.csv')
    recipeNamesTups = load_names('full_dataset.csv')
    # print(recipeNamesTups[0][1])
    # breakpoint()

    # cleanSentences = []
    vocab = set()
    # exclude = ["but", "peanuts", "and", "then", "there", "to", "than", "on", "the", "is", "too", "are", "my", "has", "not", " ", "also", "of", "a"]

    # find the longest recipe length so that we can pad the vectors 
    longest = 0

    # clean the sentences 
    for sentence in sentences:
        sentence = sentence.replace('.', '')
        sentence = sentence.replace(',', '')

        sentenceList = sentence.split(' ')

        length = 0
        for word in sentenceList:
            length += 1
            vocab.add(word)

        if length > longest:
            longest = length

    # print(longest)
    # breakpoint()
            
    # print(sentences)
    # breakpoint()

    # get vocabSize 
    vocabSize = len(vocab)

    onehotVecs = [one_hot(words, vocabSize) for words in sentences]
    # print(onehotVecs)
    # breakpoint()

    # add padding to the vectors at the end
    embeddedVectors = pad_sequences(onehotVecs, padding = 'post', maxlen = longest)

    # set dimensions 
    dimensions = 10

    # define model and compile
    model = Sequential()
    model.add( Embedding(vocabSize, dimensions, input_length = longest) )
    model.compile("adam", "mse")

    # print the model
    model.summary()
    trainedModel = model.predict(embeddedVectors)

    query = "fish tacos"
    # queryOneHot = [one_hot(query, vocabSize)]
    # embeddedQuery = pad_sequences(queryOneHot, padding = 'post', maxlen = longest)

    # finalQuery = model.predict(embeddedQuery)
    # print(finalQuery)
    # breakpoint()
    queryList = query.split(" ")

    queryIndex = -1
    for i in range(len(recipeNamesTups)):
        name = recipeNamesTups[i][0]
        nameList = name.split(" ")
        
        for word in queryList:
            if word in nameList:
                queryIndex = i
    
    # print(queryIndex)
    # breakpoint()

    if queryIndex == -1:
        for i in range(len(recipeNamesTups)):
            ingredients = recipeNamesTups[i][1]
            ingredientsList = ingredients.split(" ")
            
            for word in queryList:
                if word in ingredientsList:
                    queryIndex = i


    finalQuery = trainedModel[queryIndex]

    # Initialize variables to store the highest values
    highest_values = [0] * 3

    # get 3 highest similarities 
    index = 0
    indexList = []
    for model in trainedModel:
        similarity_score = cosine_similarity(model,  finalQuery) #trainedModel[1368]) # query

        # Check if the current number is higher than any of the highest values
        for i, val in enumerate(highest_values):
            if similarity_score > val:
                highest_values.insert(i, similarity_score)  # Insert the new highest value
                highest_values.pop()  # Remove the lowest value from the list

                indexList.append(index)
                break
                

        index += 1
        # print(index)

    
    finalIndexs = indexList[-3:]
    # print(finalIndexs)

    for index in finalIndexs:
        print(recipeNamesTups[index])



main()
