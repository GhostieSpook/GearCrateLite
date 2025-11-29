# ⚠️ Administrator-Rechte für InvDetect Scanner

## Warum werden Admin-Rechte benötigt?

Der **InvDetect Scanner** (Import from SC) benötigt erweiterte Systemrechte für folgende Funktionen:

### 1. **Tastatur-Hooks** 🎹
- Globale Tastatur-Events (INSERT, DELETE)
- `keyboard` Python-Modul benötigt Admin-Rechte
- Ohne: Scanner kann nicht gestartet/gestoppt werden

### 2. **Fenster-Switching** 🪟
- Automatisches Wechseln zu Star Citizen
- `win32gui.SetForegroundWindow()` benötigt Admin-Rechte
- Ohne: Scanner kann nicht zu SC wechseln

### 3. **Maus-Automation** 🖱️
- `pyautogui` für präzise Maus-Bewegungen
- Hover über Inventar-Items
- Drag-Scrolling im Inventar

---

## 🚀 Start-Optionen

### MIT Admin-Rechten (für Scanner):

```batch
start-browser-admin.bat    # Browser-Modus mit Admin
start-desktop-admin.bat    # Desktop-Modus mit Admin
```

### OHNE Admin-Rechte (Scanner NICHT verfügbar):

```batch
start-browser.bat          # Browser-Modus normal
start-desktop.bat          # Desktop-Modus normal
```

---

## ✅ Was funktioniert OHNE Admin-Rechte?

- ✅ Inventar-Verwaltung
- ✅ Gear Sets
- ✅ Bulk Import von Cornerstone
- ✅ Suche & Filter
- ✅ Statistiken
- ✅ Alle anderen Features

## ❌ Was funktioniert NICHT ohne Admin-Rechte?

- ❌ **Import from SC** (InvDetect Scanner)
- ❌ Automatischer Inventar-Scan
- ❌ OCR-basierte Item-Erkennung

---

## 🔒 Sicherheit

Die Admin-Rechte werden **NUR** für GearCrate verwendet:
- Keine Änderungen an Systemdateien
- Keine Netzwerk-Zugriffe außer localhost:8080
- Nur lokale Tastatur/Maus-Hooks
- Open Source - Code kann überprüft werden

---

## 📝 Empfehlung

**Für tägliche Nutzung MIT Scanner:**
```batch
start-browser-admin.bat
```

**Für schnelle Nutzung OHNE Scanner:**
```batch
start-browser.bat
```

---

## 🐛 Troubleshooting

### "Scanner startet nicht"
→ GearCrate mit Admin-Rechte starten

### "DELETE funktioniert nicht zum Abbrechen"
→ Maus in Bildschirmecke bewegen (PyAutoGUI Failsafe)

### "Kann nicht zu Star Citizen wechseln"
→ Star Citizen muss laufen BEVOR der Scan startet

---

## 📞 Support

Bei Problemen mit Admin-Rechten:
1. Rechtsklick auf Batch-Datei → "Als Administrator ausführen"
2. UAC-Dialog mit "Ja" bestätigen
3. GearCrate startet mit vollen Rechten
