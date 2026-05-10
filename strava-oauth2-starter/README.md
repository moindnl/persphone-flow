# Strava OAuth2 Starter Kit

Ein minimales, einsatzbereites Projekt mit komplettem OAuth2-Flow für die Strava API inklusive Token-Refresh.

## Schnellstart

### 1. Strava App erstellen

1. Gehe zu [Strava API Settings](https://www.strava.com/settings/api)
2. Klicke auf "Create New Application"
3. Trage folgende Daten ein:
   - **Application Name**: z.B. "Mein Strava Tool"
   - **Website URL**: `http://localhost` (für lokale Entwicklung)
   - **Authorization Domain**: `localhost`
   - **Authorization Callback Domain**: `localhost`
4. Notiere dir **Client ID** und **Client Secret**

### 2. Projekt einrichten

```bash
# Klone oder kopiere dieses Repo
cd strava-oauth2-starter

# Virtual Environment erstellen (optional)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Environment Variables konfigurieren
cp .env.example .env
# Bearbeite .env mit deinen Credentials

# App starten
python app.py
```

### 3. Testen

1. Oeffne [http://localhost:5000](http://localhost:5000) im Browser
2. Klicke auf "Connect with Strava"
3. Autorisiere die App in Strava
4. Du wirst zurückgeleitet und siehst dein Profil

## Endpunkte

| Route | Beschreibung |
|-------|--------------|
| `/` | Startseite mit Login-Button |
| `/login` | Startet OAuth-Flow (Redirect zu Strava) |
| `/callback` | Callback-Handler (von Strava aufgerufen) |
| `/profile` | Zeigt dein Strava Profil (automatischer Token-Refresh) |
| `/activities` | Zeigt deine letzten Aktivitäten |
| `/test-refresh` | Testet manuell den Token-Refresh |

## Token-Refresh

Der automatische Token-Refresh funktioniert transparent:

1. Vor jedem API-Aufruf wird geprüft, ob das Token abgelaufen ist (mit 60s Puffer)
2. Falls abgelaufen, wird automatisch ein neues Token mit dem Refresh-Token geholt
3. Das neue Token wird in `tokens.json` gespeichert
4. Falls kein Refresh-Token verfügbar ist, muss neu autorisiert werden

## Konfiguration

### Umgebungsvariablen

| Variable | Pflicht | Default | Beschreibung |
|----------|---------|---------|--------------|
| `STRAVA_CLIENT_ID` | ✅ | - | Deine Strava App Client ID |
| `STRAVA_CLIENT_SECRET` | ✅ | - | Deine Strava App Client Secret |
| `REDIRECT_URI` | ❌ | `http://localhost:5000/callback` | Callback URL für OAuth |
| `FLASK_SECRET_KEY` | ❌ | `dev-secret-change-in-production` | Flask Session Secret |

### Scopes

Passe die Scopes in `app.py` an:

```python
STRAVA_SCOPE = 'profile:read_all,activity:read_all'
```

Verfügbare Scopes: Siehe [Strava API Documentation](https://developers.strava.com/docs/authentication/#scopes)

## Token Speicherung

Standardmäßig werden Tokens in `tokens.json` gespeichert. Für Production solltest du eine sicherere Lösung verwenden, z.B.:

- **Datenbank** (SQLite, PostgreSQL, etc.)
- **Encrypted File Storage**
- **Secret Manager** (AWS Secrets Manager, HashiCorp Vault, etc.)

## Deployment

### Mit Gunicorn (Production)

```bash
pip install gunicorn
 gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Mit Docker

Erstelle eine `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build und Run:

```bash
docker build -t strava-oauth2 .
docker run -p 5000:5000 --env-file .env strava-oauth2
```

## API Beispiele

```python
from app import get_access_token, make_strava_request

# Access Token holen (automatisch refresh wenn nötig)
access_token = get_access_token()

# API Request
athlete = make_strava_request('GET', '/athlete', access_token)
activities = make_strava_request('GET', '/athlete/activities', access_token, params={'per_page': 5})
```

## Fehlerbehebung

### "redirect_uri_mismatch"
Die Redirect URI in deiner Strava App muss exakt mit `REDIRECT_URI` übereinstimmen (inkl. http/https und Port).

### "Invalid client_id or client_secret"
Prüfe, dass die Werte in `.env` korrekt sind und die Datei geladen wird.

### Token nicht gespeichert
Stelle sicher, dass das Skript Schreibrechte im Verzeichnis hat.

## Lizenz

MIT
