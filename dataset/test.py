import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('full_dataset.csv')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import nltk

# Function to clean and preprocess text
def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize text
    tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stopwords.words('english')]
    # Filter out measurement terms
    tokens = [word for word in tokens if word not in ['c', 'tsp', 'tbsp', 'oz', 'lb', 'cup', 'teaspoon', 'tablespoon', 'ounce', 'pound']]
    return ' '.join(tokens)

# Apply the cleaning function to ingredients and directions
df['ingredients_cleaned'] = df['ingredients'].apply(clean_text)
df['directions_cleaned'] = df['directions'].apply(clean_text)

# Import necessary libraries for visualization
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Visualize the most common ingredients
ingredients_text = ' '.join(df['ingredients_cleaned'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(ingredients_text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.title('Word Cloud of Ingredients')
plt.axis('off')
plt.show()
