আপনার চাহিদার অনুযায়ী **এড (Add) ফিচার** এবং **এডমিন প্যানেলে কন্ট্রোল করার সুবিধা** যোগ করে দিলাম। এখানে আপনি মুভি, সিরিজ এবং তাদের কোয়ালিটি এবং ইপিসোডগুলি **এড (Add)** করতে পারবেন, সেই সাথে **এডমিন প্যানেলে কন্ট্রোল** করতে পারবেন।

### **Complete Flask Application with Add Features & Admin Panel**

```python
import os
import requests
from flask import Flask, render_template_string, redirect, url_for, request, session
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.movie_database
movies_collection = db.movies

# TMDB API setup
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"

# Function to fetch and store movies and series in MongoDB
def fetch_and_store_data():
    # Fetch popular movies
    movie_url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(movie_url)
    movies = response.json()['results']

    # Fetch popular TV series (web series)
    series_url = f"{TMDB_BASE_URL}/tv/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(series_url)
    series = response.json()['results']

    # Save movies and series to MongoDB
    for movie in movies:
        if movies_collection.count_documents({'id': movie['id']}) == 0:
            movies_collection.insert_one({
                'id': movie['id'],
                'title': movie['title'],
                'poster_path': movie['poster_path'],
                'overview': movie['overview'],
                'release_date': movie['release_date'],
                'type': 'movie',
                'quality': []  # Initially, no quality added
            })
    
    for serie in series:
        if movies_collection.count_documents({'id': serie['id']}) == 0:
            movies_collection.insert_one({
                'id': serie['id'],
                'title': serie['name'],
                'poster_path': serie['poster_path'],
                'overview': serie['overview'],
                'release_date': serie['first_air_date'],
                'type': 'series',
                'quality': [],  # Initially, no quality added
                'episodes': []  # Episodes list
            })

# Home route to display movies and series
@app.route('/')
def home():
    fetch_and_store_data()  # Fetch data and store in DB
    movies_and_series = list(movies_collection.find())
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Movie & Series Website</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                text-align: center;
            }

            #movie-list {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }

            .movie-card {
                background-color: #fff;
                margin: 10px;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 200px;
                text-align: center;
            }

            .movie-card img {
                width: 100%;
                border-radius: 8px;
            }

            .movie-card h3 {
                margin: 10px 0;
                font-size: 1.2em;
            }

            #movie-detail {
                text-align: left;
                width: 80%;
                margin: 0 auto;
            }

            #movie-detail img {
                width: 300px;
                float: left;
                margin-right: 20px;
            }

            a {
                text-decoration: none;
                color: #007BFF;
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <h1>Popular Movies & Series</h1>
        <div id="movie-list">
            {% for item in items %}
                <div class="movie-card">
                    <a href="/movie/{{ item['id'] }}">
                        <img src="{{ img_url }}{{ item['poster_path'] }}" alt="{{ item['title'] }}">
                        <h3>{{ item['title'] }}</h3>
                        <p>{{ item['overview'][:150] }}...</p>
                    </a>
                </div>
            {% endfor %}
        </div>
        {% if session.get('logged_in') %}
        <a href="/admin">Go to Admin Panel</a>
        {% else %}
        <a href="/login">Login as Admin</a>
        {% endif %}
    </body>
    </html>
    """
    
    return render_template_string(HTML_TEMPLATE, items=movies_and_series, img_url=TMDB_IMG_URL)

# Movie/Series Detail Route
@app.route('/movie/<int:item_id>')
def movie_detail(item_id):
    item = movies_collection.find_one({'id': item_id})
    
    HTML_DETAIL_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ item['title'] }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                text-align: center;
            }

            #movie-detail {
                text-align: left;
                width: 80%;
                margin: 0 auto;
            }

            #movie-detail img {
                width: 300px;
                float: left;
                margin-right: 20px;
            }

            a {
                text-decoration: none;
                color: #007BFF;
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <h1>{{ item['title'] }}</h1>
        <div id="movie-detail">
            <img src="{{ img_url }}{{ item['poster_path'] }}" alt="{{ item['title'] }}">
            <p><strong>Release Date:</strong> {{ item['release_date'] }}</p>
            <p><strong>Overview:</strong> {{ item['overview'] }}</p>
            <h3>Available Qualities:</h3>
            {% if item['quality'] %}
                <ul>
                {% for quality in item['quality'] %}
                    <li>{{ quality }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No quality available.</p>
            {% endif %}
            <h3>Episodes (for Series):</h3>
            {% if item['type'] == 'series' %}
                <ul>
                {% for episode in item['episodes'] %}
                    <li>Episode {{ episode['episode_number'] }}: {{ episode['title'] }} - Available in: {{ episode['quality'] | join(', ') }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>This is a movie, no episodes available.</p>
            {% endif %}
        </div>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """
    
    return render_template_string(HTML_DETAIL_TEMPLATE, item=item, img_url=TMDB_IMG_URL)

# Admin Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials, try again."
    
    return '''
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

# Admin Panel Route (only accessible if logged in)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        type_ = request.form.get('type')
        release_date = request.form.get('release_date')
        overview = request.form.get('overview')
        
        if type_ == 'movie':
            new_movie = {
                'title': title,
                'type': 'movie',
                'release_date': release_date,
                'overview': overview,
                'quality': [],
                'poster_path': '',
            }
            movies_collection.insert_one(new_movie)
            return redirect(url_for('admin'))
        
        elif type_ == 'series':
            new_series = {
```
