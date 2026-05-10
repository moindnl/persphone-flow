"""
Strava OAuth2 Starter Kit
Kompletter OAuth2-Flow mit Token-Refresh für die Strava API
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, redirect, session, url_for, render_template_string
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-in-production')

# Strava OAuth2 Config
STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:5000/callback')
STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'
STRAVA_API_URL = 'https://www.strava.com/api/v3'

# Scope - anpassen nach Bedarf
STRAVA_SCOPE = 'profile:read_all,activity:read_all'


def save_tokens(athlete_id, tokens):
    """Tokens in Datei speichern (einfachste Lösung für Demo)"""
    tokens['expires_at'] = int((datetime.now() + timedelta(seconds=tokens['expires_in'])).timestamp())
    token_data = {
        'athlete_id': athlete_id,
        'access_token': tokens['access_token'],
        'refresh_token': tokens.get('refresh_token'),
        'expires_at': tokens['expires_at']
    }
    with open('tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    return token_data


def load_tokens():
    """Tokens aus Datei laden"""
    if os.path.exists('tokens.json'):
        with open('tokens.json', 'r') as f:
            return json.load(f)
    return None


def refresh_access_token(refresh_token):
    """Access Token mit Refresh Token erneuern"""
    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(STRAVA_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


def get_access_token():
    """Gültiges Access Token holen (automatisch refreshen wenn nötig)"""
    tokens = load_tokens()
    if not tokens:
        return None
    
    # Check if token is expired (with 60s buffer)
    if tokens.get('expires_at', 0) < (datetime.now() - timedelta(seconds=60)).timestamp():
        if 'refresh_token' in tokens:
            print("Token abgelaufen - refreshe...")
            new_tokens = refresh_access_token(tokens['refresh_token'])
            # Merge new tokens with old data
            tokens['access_token'] = new_tokens['access_token']
            tokens['expires_at'] = int((datetime.now() + timedelta(seconds=new_tokens['expires_in'])).timestamp())
            if 'refresh_token' in new_tokens:
                tokens['refresh_token'] = new_tokens['refresh_token']
            save_tokens(tokens['athlete_id'], tokens)
        else:
            return None
    
    return tokens['access_token']


def make_strava_request(method, endpoint, access_token, **kwargs):
    """Request an Strava API Endpoint"""
    url = f"{STRAVA_API_URL}{endpoint}"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response.json()


@app.route('/')
def index():
    """Startseite mit Login-Button"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Strava OAuth2 Demo</title></head>
    <body>
        <h1>Strava OAuth2 Starter Kit</h1>
        <p><a href="/login"><img src="https://strava.github.io/images/connect-with-strava.png" alt="Connect with Strava"></a></p>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/login')
def login():
    """Redirect zu Strava OAuth Autorisierung"""
    params = {
        'client_id': STRAVA_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'approval_prompt': 'auto',
        'scope': STRAVA_SCOPE
    }
    auth_url = f"{STRAVA_AUTH_URL}?" + '&'.join([f"{k}={v}" for k, v in params.items()])
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Callback Handler - tauscht Code gegen Token"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"Fehler bei der Autorisierung: {error}", 400
    
    if not code:
        return "Kein Authorization Code erhalten", 400
    
    # Token Request
    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(STRAVA_TOKEN_URL, data=data)
    response.raise_for_status()
    tokens = response.json()
    
    # Athlete Info holen
    access_token = tokens['access_token']
    athlete = make_strava_request('GET', '/athlete', access_token)
    athlete_id = athlete['id']
    
    # Tokens speichern
    save_tokens(athlete_id, tokens)
    
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    """Zeige Benutzerprofil (benötigt gültiges Token)"""
    access_token = get_access_token()
    if not access_token:
        return redirect(url_for('login'))
    
    athlete = make_strava_request('GET', '/athlete', access_token)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Profil</title></head>
    <body>
        <h1>Dein Strava Profil</h1>
        <img src="{{ profile_img }}" width="100">
        <h2>{{ name }}</h2>
        <p>ID: {{ athlete_id }}</p>
        <p>Stadt: {{ city }}</p>
        <p>Land: {{ country }}</p>
        <p><a href="/activities">Aktivitäten anzeigen</a></p>
        <p><a href="/">Zurück</a></p>
    </body>
    </html>
    '''
    return render_template_string(
        html,
        profile_img=athlete.get('profile', ''),
        name=athlete.get('firstname', '') + ' ' + athlete.get('lastname', ''),
        athlete_id=athlete.get('id', ''),
        city=athlete.get('city', ''),
        country=athlete.get('country', '')
    )


@app.route('/activities')
def activities():
    """Zeige letzte Aktivitäten"""
    access_token = get_access_token()
    if not access_token:
        return redirect(url_for('login'))
    
    activities = make_strava_request('GET', '/athlete/activities', access_token, params={'per_page': 10})
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Aktivitäten</title></head>
    <body>
        <h1>Deine letzten Aktivitäten</h1>
        <p><a href="/profile">Zurück zum Profil</a></p>
        <ul>
            {% for activity in activities %}
            <li>
                <strong>{{ activity.name }}</strong> - {{ activity.type }}<br>
                Distanz: {{ "%.1f"|format(activity.distance / 1000) }} km<br>
                Dauer: {{ "%.1f"|format(activity.moving_time / 60) }} min<br>
                Datum: {{ activity.start_date_local[:10] }}
            </li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''
    from jinja2 import Template
    template = Template(html)
    return template.render(activities=activities)


@app.route('/test-refresh')
def test_refresh():
    """Teste manuell den Token Refresh"""
    tokens = load_tokens()
    if not tokens or 'refresh_token' not in tokens:
        return "Kein Refresh Token verfügbar", 400
    
    new_tokens = refresh_access_token(tokens['refresh_token'])
    return f"Neues Token erhalten! Expires in: {new_tokens['expires_in']} Sekunden"


if __name__ == '__main__':
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        print("FEHLER: STRAVA_CLIENT_ID und STRAVA_CLIENT_SECRET müssen gesetzt sein!")
        print("Kopiere .env.example nach .env und trage deine Werte ein.")
        exit(1)
    
    print("Starte Server auf http://localhost:5000")
    print("Oeffne die URL im Browser und klicke auf 'Connect with Strava'")
    app.run(debug=True, port=5000)
