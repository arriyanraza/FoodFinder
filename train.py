import numpy as np
import re
import ast
import pandas as pd
import tensorflow
from tensorflow.keras.preprocessing.text import one_hot

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

def buildVocab(sentences):
    
    # Build vocabulary
    vocab = set()
    for sentence in tokenized_corpus:
        for word in sentence:
            vocab.add(word)
    word_to_index = {word: i for i, word in enumerate(vocab)}
    index_to_word = {i: word for i, word in enumerate(vocab)}
    vocab_size = len(vocab)

def main():
        
    sentences = load_data('small_dataset.csv')
    print(sentences)



    onehot_vecs = [one_hot(words, vocabSize) for words in sentences]

main()