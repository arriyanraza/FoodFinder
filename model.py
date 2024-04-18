import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import re

# Function to load and preprocess data from CSV
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    recipes = data['title']
    ingredients_list = data['ingredients'].apply(ast.literal_eval)  # Convert ingredients from string to list
    combined_texts = []

    for _, row in data.iterrows():
        ingredients = ast.literal_eval(row['ingredients'])
        directions = ast.literal_eval(row['directions'])
        recipe_title = row['title']
        combined_text = recipe_title + ' ' + ' '.join(ingredients) + ' ' + ' '.join(directions)
        combined_texts.append(clean_text(combined_text))

    return combined_texts, recipes, ingredients_list

# Clean and prepare text
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    return text

# Create TF-IDF model and vectorize texts
def vectorize_texts(texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix, vectorizer

# Find the top closest matches for a query
def find_top_matches(query, vectorizer, tfidf_matrix, recipes, ingredients, top_n=3):
    query_vec = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(-cosine_similarities)[:top_n]
    matches = [(recipes.iloc[i], ingredients.iloc[i], cosine_similarities[i]) for i in top_indices]
    return matches

# Main function to run the program
def main():
    csv_file = './dataset/full_dataset.csv'  # specify the path to your CSV file
    text_data, recipes, ingredients_list = load_data(csv_file)
    tfidf_matrix, vectorizer = vectorize_texts(text_data)

    # Example query
    query = "macaroni and cheese pizza"
    matches = find_top_matches(query, vectorizer, tfidf_matrix, recipes, ingredients_list)
    
    print(f"Top {len(matches)} matches for '{query}':")
    for title, ingredients, score in matches:
        print(f"\nTitle: {title}")
        #print(f"Score: {score:.4f}")
        print("Ingredients:")
        for ingredient in ingredients:
            print(f"  - {ingredient}")

# Run the main program
if __name__ == "__main__":
    main()
