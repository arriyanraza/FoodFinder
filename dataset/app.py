from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import ast  # Ensure ast is imported

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ingredients = db.Column(db.String(1024), nullable=False)  # Store as JSON string

    def __repr__(self):
        return f'<Recipe {self.title}>'

def create_tables():
    db.create_all()

def load_data():
    data = pd.read_csv('full_dataset.csv')
    for index, row in data.iterrows():
        # Ensure to parse the 'NER' field correctly as a list
        ingredients_str = ','.join(ast.literal_eval(row['NER']))
        recipe = Recipe(title=row['title'], ingredients=ingredients_str)
        db.session.add(recipe)
    db.session.commit()

def find_recipes(user_ingredients):
    matched_recipes = []
    user_ingredients_set = set(user_ingredients)
    all_recipes = Recipe.query.all()
    for recipe in all_recipes:
        ingredients_set = set(recipe.ingredients.split(','))
        match_count = len(ingredients_set & user_ingredients_set)
        if match_count > 0:
            matched_recipes.append({"title": recipe.title, "match_count": match_count})
    matched_recipes.sort(key=lambda x: x['match_count'], reverse=True)
    return matched_recipes[:5]  # Return top 5 matches

@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    user_ingredients = request.json.get('ingredients', [])
    matched_recipes = find_recipes(user_ingredients)
    return jsonify(matched_recipes)

if __name__ == "__main__":
    with app.app_context():
        create_tables()
        if not Recipe.query.first():  # Check if the database is empty
            load_data()
    app.run(debug=True, port=5000)
