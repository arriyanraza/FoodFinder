import pandas as pd
import numpy as np
import gensim
import ast
import re

# Function to load and preprocess data from CSV
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    recipes = data['title']
    ingredients_list = data['ingredients'].apply(ast.literal_eval)  # Convert ingredients from string to list
    combined_texts = []

    for _, row in data.iterrows():
        ingredients = ast.literal_eval(row['NER'])
        recipe_title = row['title']
        combined_text = recipe_title + ' ' + ' '.join(ingredients) 
        combined_texts.append(clean_text(combined_text))

    return combined_texts, recipes, ingredients_list

# Clean and prepare text
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    return text

# Function to tokenize text
def tokenize_text(texts):
    tokenized_texts = [text.split() for text in texts]
    return tokenized_texts

# Train Word2Vec model
def train_word2vec_model(tokenized_texts):
    model = gensim.models.Word2Vec(sentences=tokenized_texts, vector_size=300, window=5, min_count=1, workers=4)
    return model

# Function to calculate document embeddings
def document_embedding(text, model):
    words = [word for word in text.split() if word in model.wv]  # Check if word is in the model's vocabulary
    if len(words) == 0:
        return np.zeros(model.vector_size)
    word_vectors = [model.wv[word] for word in words]  # Access word vectors for words in the model's vocabulary
    return np.mean(word_vectors, axis=0)


# Find the top closest matches for a query
def find_top_matches(query, model, recipes, ingredients_list, top_n=3):
    query_vec = document_embedding(query, model)
    ingredients_str = ' '.join([str(ingredient) for ingredient in ingredients_list])
    recipe_vecs = [document_embedding(' '.join(ingredients), model) for ingredients in ingredients_list]
    similarities = [np.dot(query_vec, recipe_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(recipe_vec)) for recipe_vec in recipe_vecs]
    top_indices = np.argsort(-np.array(similarities))[:top_n]
    matches = [(recipes.iloc[i], ingredients_list.iloc[i], similarities[i]) for i in top_indices]
    return matches

# Main function to run the program
def main():
    csv_file = 'full_dataset.csv'  # specify the path to your CSV file
    text_data, recipes, ingredients_list = load_data(csv_file)
    tokenized_texts = tokenize_text(text_data)
    model = train_word2vec_model(tokenized_texts)

    while True:
        query = input("Enter your query (type 'quit' to exit): ")
        if query.lower() == 'quit':
            print("Goodbye!")
            break
        
        matches = find_top_matches(query, model, recipes, ingredients_list)
        print(f"Top {len(matches)} matches for '{query}':")
        for title, ingredients, score in matches:
            print(f"\nTitle: {title}")
            print("Ingredients:")
            for ingredient in ingredients:
                print(f"  - {ingredient}")

# Run the main program
if __name__ == "__main__":
    main()
