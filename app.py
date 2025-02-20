from flask import Flask, request, render_template, redirect, url_for, session
from psycopg2 import Error
# from keras.models import load_model
from google_auth_oauthlib.flow import Flow
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from bs4 import BeautifulSoup
import requests
# from sklearn.ensemble import RandomForestRegressor
import joblib
from authlib.integrations.flask_client import OAuth
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import IntegrityError

#ml code
def calculate_title_importance(title, query):
    title = title.lower()
    query = query.lower()
    query_words = query.split()
    count = sum(word in title for word in query_words)
    importance = count / len(query_words)
    return importance

def calculate_headers_importance(headers, query):
    query = query.lower()
    query_words = query.split()
    total_importance = 0
    for header in headers:
        header = header.lower()
        count = sum(word in header for word in query_words)
        importance = count / len(query_words)
        total_importance += importance
    return total_importance

def calculate_body_text_importance(body_text, query):
    body_text = body_text.lower()
    query = query.lower()
    query_words = query.split()
    body_text_words = body_text.split()
    count = sum(word in body_text_words for word in query_words)
    importance = count / len(query_words)
    return importance

def calculate_alt_text_for_images_importance(alt_text_for_images, query):
    alt_text_for_images = alt_text_for_images.lower()
    query = query.lower()
    query_words = query.split()
    count = sum(word in alt_text_for_images for word in query_words)
    importance = count / len(query_words)
    return importance

def calculate_backlinks_importance(backlinks):
    importance = len(backlinks)
    return importance

def calculate_meta_tags_importance(meta_tags, query):
    meta_tags = meta_tags.lower()
    query = query.lower()
    query_words = query.split()
    count = sum(word in meta_tags for word in query_words)
    importance = count / len(query_words)

    return importance

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect(
        dbname='dhp2024',
        user='postgres',
        password='1805',
        host='localhost'
    )
    cur = conn.cursor()

    # Create users table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(100) PRIMARY KEY,
            name VARCHAR(100),
            password VARCHAR(100)
        )
    """)
    conn.commit()

    # Create website_info table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS website_info (
            id SERIAL PRIMARY KEY,
            URL TEXT,
            query TEXT,
            rank INTEGER,
            title_importance INTEGER,
            headers_importance INTEGER,
            body_text_importance INTEGER,
            meta_tags_importance INTEGER,
            alt_text_for_images_importance INTEGER
        )
    """)
    conn.commit()

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL:", error)
# finally:
#     # Close database connection
#     if conn:
#         cur.close()
#         conn.close()


app = Flask(__name__)
# Load your trained model and scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

app.secret_key = 'pdai_kro_beta'
oauth = OAuth(app)
# Path to the client secrets file
client_secrets_file = 'client_secret_996742358754-gtl6du3qvfpknpcr4fb4luoaub1k5tjt.apps.googleusercontent.com.json'

# Scopes define the level of access you are requesting from the user
scopes = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']

# Redirect URI for the OAuth flow
redirect_uri = 'http://127.0.0.1:5000/callback'

# Create the OAuth flow object
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)

# To Google login
@app.route('/login/google')
def google():
    if 'google_token' in session:
        # User is already authenticated, redirect to a protected route
        return redirect(url_for('protected'))
    else:
        # User is not authenticated, render the ggl.html template
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)
# Callback route for handling OAuth response
@app.route('/callback')
def callback():
    # Handle the callback from the Google OAuth flow
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token

    # Redirect to the protected route or another page
    return redirect(url_for('protected'))

# Protected route accessible only to authenticated users

@app.route('/protected')
def protected():
    if 'google_token' in session:
        # User is authenticated
        # Get the user's email from the Google API
        userinfo = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {session["google_token"]}'})
        email = userinfo.json().get('email')
    
        return render_template("index.html")
    else:
        # User is not authenticated
        return render_template("index.html")

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logo')
def logo():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('adminlogin.html')

# Define routes for sign-up and login
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            # Execute SQL INSERT command to add new user to the database
            cur.execute("INSERT INTO users (email, name, password) VALUES (%s, %s, %s)", (email, name, password))
            conn.commit()
            return render_template('login.html')  # Redirect to homepage or login page
        except IntegrityError:
            # Handle unique constraint violation (if email already exists)
            conn.rollback()
            # return "Email already exists. Please use a different email address."
            return render_template('login.html',signup_error='Email already exist.')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database for the user with the provided email
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        # If user exists and password is correct, set session and redirect
        if user and user[2] == password:
            session['user_email'] = email
            return render_template('index.html')  # Redirect to homepage or dashboard
        else:
            # return "Invalid email or password. Please try again."
            return render_template('login.html',error='Invalid Email or password')

@app.route('/signout')
def signout():
    # Clear the user's session data
    session.clear()
    # Redirect the user to the login page
    return redirect(url_for('index'))



@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        url = request.form.get('url')
        query = request.form.get('query')

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('title').text if soup.find('title') else 'N/A'
        headers = [h.text for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])] if soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) else 'N/A'
        body_text = soup.find('body').text if soup.find('body') else 'N/A'
        meta_tags = ', '.join([meta['content'] for meta in soup.find_all('meta') if 'content' in meta.attrs]) if soup.find_all('meta') else 'N/A'
        alt_text_for_images = ', '.join([img['alt'] for img in soup.find_all('img') if 'alt' in img.attrs]) if soup.find_all('img') else 'N/A'
        backlinks = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')] if soup.find_all('a', href=True) else 'N/A'
        title_importance = calculate_title_importance(title, query)
        headers_importance = calculate_headers_importance(headers, query)
        body_text_importance = calculate_body_text_importance(body_text, query)
        meta_tags_importance = calculate_meta_tags_importance(meta_tags, query)
        alt_text_for_images_importance = calculate_alt_text_for_images_importance(alt_text_for_images, query)
        pagespeed_response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}")
        loading_speed_score = pagespeed_response.json()['lighthouseResult']['audits']['speed-index']['displayValue'] if 'lighthouseResult' in pagespeed_response.json() and 'audits' in pagespeed_response.json()['lighthouseResult'] and 'speed-index' in pagespeed_response.json()['lighthouseResult']['audits'] else 'N/A'
        loading_speed_score = loading_speed_score.replace('\xa0s', '')
        loading_speed_score = float(loading_speed_score)
        backlinks_importance = calculate_backlinks_importance(backlinks)

        X_normalized = np.array([headers_importance, loading_speed_score, backlinks_importance])

        X_normalized = scaler.transform(X_normalized.reshape(1, -1))

        X_non_normalized = np.array([title_importance, body_text_importance, meta_tags_importance, alt_text_for_images_importance])

        X_non_normalized = X_non_normalized.reshape(1, -1)

        X = np.concatenate((X_normalized, X_non_normalized), axis=1)

        rank = model.predict(X)
        
        try:
            conn = psycopg2.connect(
                dbname='dhp2024',
                user='postgres',
                password='1805',
                host='localhost'
            )
            cursor = conn.cursor()

            insert_query = '''INSERT INTO website_info (URL, query, rank, title_importance, headers_importance, body_text_importance, meta_tags_importance, alt_text_for_images_importance)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(insert_query, (url, query, rank[0], title_importance, X_normalized[0][0], body_text_importance, meta_tags_importance, alt_text_for_images_importance))
            conn.commit()
        except (Exception, Error) as error:
            print("Error while inserting data into PostgreSQL:", error)
        finally:
            # Close database connection
            if conn:
                cursor.close()
                conn.close()

        return render_template('index.html', rank=rank[0], title_importance=title_importance, headers_importance=X_normalized[0][0], loading_speed_score=X_normalized[0][1], backlinks_importance=X_normalized[0][2], body_text_importance=body_text_importance, meta_tags_importance=meta_tags_importance, alt_text_for_images_importance=alt_text_for_images_importance)
    return render_template('index.html')

# Route for admin login
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        if username.lower() == 'sahil' and password == '123':
            # Redirect to history page upon successful login
            return redirect(url_for('history'))
        else:
            # Render admin login page with error message
            return render_template('adminlogin.html', error='Invalid username or password')
    else:
        return render_template('adminlogin.html', error='')


# Route for history page
@app.route('/history')
def history():
    # Fetch data from website_info table
    conn = psycopg2.connect(
        dbname='dhp2024',
        user='postgres',
        password='1805',
        host='localhost'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM website_info")
    data = cursor.fetchall()

    conn.close()

    return render_template('History.html', data=data)



if __name__ == '__main__':
    app.run(debug=True)



