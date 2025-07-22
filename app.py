import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# TMDB API Key & URL
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"

# Home route to fetch popular movies
@app.route('/')
def home():
    url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    movies = response.json()['results']
    return render_template('index.html', movies=movies, img_url=TMDB_IMG_URL)

# Search route for movies
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US&page=1"
        response = requests.get(url)
        movies = response.json()['results']
        return render_template('search_results.html', movies=movies, img_url=TMDB_IMG_URL)
    return render_template('search_results.html', movies=[], img_url=TMDB_IMG_URL)

# Movie detail route
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    movie = response.json()
    return render_template('movie_detail.html', movie=movie, img_url=TMDB_IMG_URL)

if __name__ == '__main__':
    app.run(debug=True)
