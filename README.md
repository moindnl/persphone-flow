# [Strava OAuth2 Starter Kit](./strava-oauth2-starter)

Ein kompaktes, einsatzbereites Starter-Kit mit komplettem OAuth2-Flow für die Strava API inklusive automatischem Token-Refresh.

**Features:**
- ✅ Authorization Code Grant Flow
- ✅ Automatischer Token-Refresh mit Puffer (60s)
- ✅ Flask Webserver mit Demo-UI
- ✅ Profil- und Aktivitäten-Ansicht
- ✅ Environment Variable Konfiguration
- ✅ Docker-Ready

**Schnellstart:**

```bash
cd strava-oauth2-starter
pip install -r requirements.txt
cp .env.example .env
# .env mit deinen Strava Credentials füllen
python app.py
```

Dann [http://localhost:5000](http://localhost:5000) öffnen.

**Strava App erstellen:** [https://www.strava.com/settings/api](https://www.strava.com/settings/api)

---

## 🎯 Ziel

Dieses Repository soll eine Sammlung von praxisnahen Implementierungen sein, die Entwicklern den Einstieg in verschiedene APIs erleichtern.

## 🤝 Mitwirken

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue erstellen, um die Änderungen abzustimmen.

## 📄 Lizenz

Alle Projekte in diesem Repository unterliegen der [MIT License](LICENSE).
