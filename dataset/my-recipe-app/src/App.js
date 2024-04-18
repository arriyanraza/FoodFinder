import React, { useState } from 'react';
import './App.css';

function App() {
  const [ingredients, setIngredients] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [isVegetarian, setIsVegetarian] = useState(false);

  const fetchRecipes = async () => {
    try {
      const ingredientsText = ingredients.split(/[, ]+/).filter(Boolean).join(' ');
      const requestBody = {
        ingredients: ingredientsText,
        vegetarian: isVegetarian
      };

      const response = await fetch('http://127.0.0.1:5000/api/recipes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      setRecipes(data);
    } catch ( error ) {
      console.error('Failed to fetch recipes:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>The Food Rec</h1>
        <input
          type="text"
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
          placeholder="Enter ingredients separated by commas"
        />
        <div className="switch">
          <input
            type="checkbox"
            id="veg-toggle"
            checked={isVegetarian}
            onChange={() => setIsVegetarian(!isVegetarian)}
          />
          <span className="slider"></span>
        </div>
        <label htmlFor="veg-toggle">Vegetarian Only</label>
        <button onClick={fetchRecipes}>Get Recipes</button>
        <ul className="recipe-list">
  {recipes.map((recipe, index) => (
    <li key={index} className="recipe-item">
      <img src={recipe.image} alt={recipe.title} style={{ width: '200px', height: '200px' }} />
      <h3>{recipe.title} - Matches: {recipe.score.toFixed(2)}</h3>
      <div>Ingredients:</div>
      <ul className="ingredients-list">
        {recipe.ingredients.map((ingredient, idx) => (
          <li key={idx}>{ingredient}</li>
        ))}
      </ul>
      <p>{recipe.is_vegetarian ? "Suitable for Vegetarians" : "Includes Meat"}</p>
      <a href={recipe.link} target="_blank" rel="noopener noreferrer">View Recipe</a>
    </li>
  ))}
</ul>

      </header>
    </div>
  );
}

export default App;
