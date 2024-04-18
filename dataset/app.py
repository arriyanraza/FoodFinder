from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
import numpy as np
import ast
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

meat_ingredients = ['chicken', 'beef', 'pork', 'ham', 
                    'turkey', 'lamb', 'duck', 'sausage', 'bacon', 'pepperoni',
                    'ground beef', 'hamburger', 'ground round', 'beef brisket',
                    'ground chuck', 'hen']

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ingredients = db.Column(db.String(1024), nullable=False)
    link = db.Column(db.String(1024), nullable=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

def load_data():
    data = pd.read_csv('full_dataset.csv')
    combined_texts = [clean_text(row['title'] + ' ' + ' '.join(ast.literal_eval(row['ingredients'])))
                      for index, row in data.iterrows()]
    return combined_texts, data['title'], data['ingredients'].apply(ast.literal_eval), data['link']

def setup_tfidf():
    texts, titles, ingredients, links = load_data()  # Adjust here to unpack four values
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer, tfidf_matrix, titles, ingredients, links  # Return links as well

def fetch_image(query):
    api_url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "client_id": "btzgwBHJZIRCcV-Z9GBG34tUkX9_tHNWWvrubnvWfx4",  # Your Access Key
        "per_page": 1
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']  # Get the URL of the first image
    return "default-image-url.jpg" 

def find_top_matches(query, vectorizer, tfidf_matrix, titles, ingredients, links, vegetarian=False):
    query_vec = vectorizer.transform([clean_text(query)])
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(-cosine_similarities)[:5]
    matches = []
    for i in top_indices:
        recipe_ingredients = ingredients.iloc[i]
        contains_meat = any(meat in ' '.join(recipe_ingredients) for meat in meat_ingredients)
        if vegetarian and contains_meat:
            continue
        link = links.iloc[i]
        if not link.startswith(('http://', 'https://')):
            link = 'http://' + link
        image_url = fetch_image(titles.iloc[i])
        matches.append({
            "title": titles.iloc[i],
            "ingredients": recipe_ingredients,
            "score": cosine_similarities[i],
            "link": link,
            "image": image_url,
            "is_vegetarian": not contains_meat
        })
    return matches


vectorizer, tfidf_matrix, titles, ingredients_list, links_list = setup_tfidf()

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    data = request.get_json()
    user_query = data.get('ingredients', '')
    vegetarian = data.get('vegetarian', False)
    matches = find_top_matches(user_query, vectorizer, tfidf_matrix, titles, ingredients_list, links_list, vegetarian=vegetarian)
    return jsonify(matches)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
