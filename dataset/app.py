from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import numpy as np
import ast
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Meat ingredients for vegetarian filtering
meat_ingredients = ['chicken', 'beef', 'pork', 'ham', 
                    'turkey', 'lamb', 'duck', 'sausage', 'bacon', 'pepperoni',
                    'ground beef', 'hamburger', 'ground round', 'beef brisket',
                    'ground chuck', 'hen']

# Database model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ingredients = db.Column(db.String(1024), nullable=False)
    link = db.Column(db.String(1024), nullable=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

# Clean and prepare text for TF-IDF
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

# Load and preprocess data
def load_data():
    data = pd.read_csv('full_dataset.csv')
    combined_texts = [clean_text(row['title'] + ' ' + ' '.join(ast.literal_eval(row['ingredients'])))
                      for index, row in data.iterrows()]
    return combined_texts, data['title'], data['ingredients'].apply(ast.literal_eval)

# Setup TF-IDF vectorization and cosine similarity
def setup_tfidf():
    texts, titles, ingredients = load_data()
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer, tfidf_matrix, titles, ingredients

# Find the top closest matches for a query
def find_top_matches(query, vectorizer, tfidf_matrix, titles, ingredients, vegetarian=False):
    query_vec = vectorizer.transform([clean_text(query)])
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(-cosine_similarities)[:5]
    matches = []
    for i in top_indices:
        recipe_ingredients = ingredients.iloc[i]
        contains_meat = any(meat in ingredient for ingredient in recipe_ingredients for meat in meat_ingredients)
        if vegetarian and contains_meat:
            continue
        matches.append({
            "title": titles.iloc[i],
            "ingredients": recipe_ingredients,
            "score": cosine_similarities[i],
            "link": "Link to recipe"  # Modify as necessary
        })
    return matches

vectorizer, tfidf_matrix, titles, ingredients_list = setup_tfidf()

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    data = request.get_json()
    user_query = data.get('ingredients', '')
    vegetarian = data.get('vegetarian', False)
    matches = find_top_matches(user_query, vectorizer, tfidf_matrix, titles, ingredients_list, vegetarian=vegetarian)
    return jsonify(matches)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True, port=5000)
