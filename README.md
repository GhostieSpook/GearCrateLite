# Star Citizen Inventory Manager

Ein Desktop-Tool zum Katalogisieren deiner Star Citizen Kleidung und Rüstung.

## Features

- 🔍 **Live-Suche**: Suche nach Items auf CStone.space
- 📦 **Inventar-Verwaltung**: Tracke deine Sammlung mit Bildern
- 📊 **Statistiken**: Übersicht über deine Items
- 🖼️ **Bild-Cache**: Automatisches Caching von Bildern
- 📝 **Notizen**: Füge Notizen zu Items hinzu
- 🎯 **Zähler**: Tracke wie viele von jedem Item du hast

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Setup

1. **Entpacke das Projekt** in einen Ordner deiner Wahl

2. **Installation & Start**:

   **Windows (einfach):**
   - Doppelklick auf `setup.bat` - installiert und startet automatisch
   
   Oder separat:
   - `install.bat` - Installiert nur die Dependencies
   - `start.bat` - Startet nur das Programm
   
   **Linux/Mac (manuell):**
   ```bash
   cd sc-inventory-manager
   pip install -r requirements.txt --break-system-packages
   python src/main.py
   ```

## Nutzung

### Bulk-Import von CStone.space

Du kannst ALLE Items von CStone.space auf einmal importieren:

**Option 1: Vollständiger Import (mit Bildern)**
```cmd
import-all-items.bat
```
- Importiert alle Items MIT Bildern
- Dauert länger (mehrere Minuten)
- Empfohlen wenn du alles komplett haben willst

**Option 2: Quick Import (nur Namen)**
```cmd
import-quick.bat
```
- Importiert nur Item-Namen
- Viel schneller (wenige Sekunden)
- Bilder können später über normale Suche hinzugefügt werden

### Programm starten

**Windows:** Doppelklick auf `start-browser.bat` (empfohlen) oder `start.bat`

**Linux/Mac:**
```bash
python src/main.py
```

### Bedienung

1. **Item hinzufügen**:
   - Gib den Item-Namen in die Suchleiste ein
   - Wähle ein Item aus den Suchergebnissen (CStone.space)
   - Klicke auf "Eintragen"

2. **Inventar durchsuchen**:
   - Nutze die Filterleiste um dein Inventar zu durchsuchen
   - Klicke auf ein Item für Details

3. **Item bearbeiten**:
   - Klicke auf ein Item im Inventar
   - Ändere Anzahl oder Notizen
   - Klicke auf "Speichern"

4. **Item löschen**:
   - Öffne Item-Details
   - Klicke auf "Löschen"
   - Bestätige die Löschung

## Projektstruktur

```
sc-inventory-manager/
├── src/                    # Source Code
│   ├── gui/               # GUI (pywebview)
│   ├── database/          # SQLite Datenbank
│   ├── scraper/           # CStone.space Scraper
│   ├── cache/             # Bild-Cache System
│   ├── api/               # Backend API
│   └── main.py            # Entry Point
├── web/                    # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/                   # Daten (wird erstellt)
│   ├── inventory.db       # SQLite Datenbank
│   └── cache/             # Gecachte Bilder
└── requirements.txt        # Python Dependencies
```

## Technologie-Stack

- **Backend**: Python
- **GUI**: pywebview (Webview-basiertes Desktop-UI)
- **Datenbank**: SQLite
- **Web Scraping**: BeautifulSoup4, Requests
- **Bildverarbeitung**: Pillow
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Batch-Dateien (Windows)

Das Projekt enthält mehrere Batch-Dateien für Windows-Nutzer:

- **`setup.bat`**: Installiert Dependencies und startet das Programm (für Erstnutzung)
- **`install.bat`**: Installiert nur die Dependencies
- **`start.bat`**: Startet nur das Programm
- **`clean.bat`**: Löscht Datenbank und Cache (VORSICHT: Alle Daten gehen verloren!)

## Troubleshooting

### pywebview startet nicht

Falls pywebview Probleme macht, installiere die entsprechenden WebView-Komponenten:

**Windows**: Edge WebView2 (normalerweise bereits installiert)
**Linux**: 
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.0
```
**macOS**: Nutzt WebKit (bereits integriert)

### Bilder werden nicht geladen

- Stelle sicher, dass du eine Internetverbindung hast
- CStone.space muss erreichbar sein
- Der `data/cache/images` Ordner muss beschreibbar sein

### Datenbank-Fehler

Falls die Datenbank korrupt ist:
```bash
rm data/inventory.db
```
Dann starte das Programm neu - die Datenbank wird neu erstellt.

## Lizenz

Dieses Projekt ist für den privaten Gebrauch gedacht.

## Hinweise

- Das Tool scrapt Bilder von CStone.space - bitte nutze es verantwortungsvoll
- Bilder werden lokal gecached, um Server-Last zu minimieren
- Die Datenbank ist lokal auf deinem Rechner gespeichert

## Support

Bei Problemen oder Fragen erstelle ein Issue auf GitHub oder melde dich direkt.

---

**Viel Spaß beim Katalogisieren deiner Star Citizen Sammlung! 🚀**
