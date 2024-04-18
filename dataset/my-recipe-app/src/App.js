import React, { useState } from 'react';
import './App.css';

function App() {
  const [ingredients, setIngredients] = useState('');
  const [recipes, setRecipes] = useState([]);

  const fetchRecipes = async () => {
    const ingredientsArray = ingredients.split(/[, ]+/).filter(Boolean);
    const response = await fetch('http://127.0.0.1:5000/api/recipes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ingredients: ingredientsArray })
    });
    const data = await response.json();
    const updatedData = data.map(recipe => {
        return {
            ...recipe,
            link: recipe.link.startsWith('http') ? recipe.link : `http://${recipe.link}`
        };
    });
    setRecipes(updatedData);
};

  return (
    <div className="App">
      <header className="App-header">
        <input
          type="text"
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
          placeholder="Enter ingredients separated by commas"
        />
        <button onClick={fetchRecipes}>Get Recipes</button>
        <ul>
          {recipes.map((recipe, index) => (
            <li key={index}>
              {recipe.title} - Matches: {recipe.match_count}<br/>
              Ingredients: {recipe.all_ingredients}<br/>
              <a href={recipe.link} target="_blank" rel="noopener noreferrer">View Recipe</a>
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}


export default App;