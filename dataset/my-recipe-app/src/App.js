import React, { useState } from 'react';
import './App.css';

function App() {
  const [ingredients, setIngredients] = useState('');
  const [recipes, setRecipes] = useState([]);

  const fetchRecipes = async () => {
    // Split by commas or spaces, or add more delimiters as needed
    const ingredientsArray = ingredients.split(/[, ]+/).filter(Boolean);
  
    const response = await fetch('http://127.0.0.1:5000/api/recipes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ingredients: ingredientsArray })
    });
  
    const data = await response.json();
    setRecipes(data);
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
            <li key={index}>{recipe.title} - Matches: {recipe.match_count}</li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
