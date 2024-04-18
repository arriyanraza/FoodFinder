from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import ast
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
meat_ingredients = ['chicken', 'beef', 'pork', 'ham', 
                    'turkey', 'lamb', 'duck', 'sausage', 'bacon', 'pepperoni',
                    'ground beef', 'hamburger', 'ground round', 'beef brisket']

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ingredients = db.Column(db.String(1024), nullable=False)
    link = db.Column(db.String(1024), nullable=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

def create_tables():
    db.create_all()

def load_data():
    data = pd.read_csv('full_dataset.csv')
    for index, row in data.iterrows():
        ingredients_str = ','.join(ast.literal_eval(row['NER']))
        link_str = f"http://{row['link']}" if 'link' in row and not row['link'].startswith(('http:', 'https:')) else row.get('link', 'default-link')
        recipe = Recipe(title=row['title'], ingredients=ingredients_str, link=link_str)
        db.session.add(recipe)
    db.session.commit()

def find_recipes(user_ingredients, vegetarian=False):
    matched_recipes = []
    user_ingredients_set = set(user_ingredients)
    all_recipes = Recipe.query.all()
    for recipe in all_recipes:
        ingredients_set = set(recipe.ingredients.split(','))
        contains_meat = any(meat in ingredients_set for meat in meat_ingredients)
        
        if vegetarian and contains_meat:
            continue  # Skip this recipe if vegetarian mode is on and recipe contains meat

        match_count = len(ingredients_set & user_ingredients_set)
        if match_count > 0:
            matched_recipes.append({
                "title": recipe.title,
                "match_count": match_count,
                "all_ingredients": recipe.ingredients,
                "link": recipe.link,
                "is_vegetarian": not contains_meat
            })

    matched_recipes.sort(key=lambda x: x['match_count'], reverse=True)
    return matched_recipes[:5]

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    data = request.get_json()
    user_ingredients = data.get('ingredients', [])
    vegetarian = data.get('vegetarian', False)  # Expect a vegetarian flag in the request
    matched_recipes = find_recipes(user_ingredients, vegetarian)
    return jsonify(matched_recipes)

if __name__ == "__main__":
    with app.app_context():
        create_tables()
        if not Recipe.query.first():  # Check if the database is empty
            load_data()
    app.run(debug=True, port=5000)
