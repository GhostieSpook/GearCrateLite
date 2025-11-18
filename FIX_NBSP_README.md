# Fix für Suchproblem mit Non-Breaking Spaces

## Problem
Items mit **Non-Breaking Spaces** (`\xa0`) im Namen konnten nicht gefunden werden, wenn mit normalem Leerzeichen gesucht wurde.

Beispiel: "TCS-4 Undersuit Black/Grey" 
- In der DB: `TCS-4 Undersuit\xa0Black/Grey` (mit non-breaking space)
- Bei Suche: `TCS-4 Undersuit Black/Grey` (mit normalem Leerzeichen)
- Resultat: ❌ Nicht gefunden

## Lösung

### 1️⃣ Datenbank bereinigen (Empfohlen)
Entfernt alle Non-Breaking Spaces aus Item-Namen in der Datenbank.

**Ausführen:**
```bash
fix-nbsp.bat
```

Dies ersetzt alle `\xa0` durch normale Leerzeichen in der Datenbank.

### 2️⃣ Suchfunktion verbessert (Bereits erledigt ✅)
Die Suchfunktion wurde angepasst, um verschiedene Leerzeichen-Arten zu normalisieren:
- Non-breaking spaces (`\xa0` / `CHAR(160)`)
- Tabs (`CHAR(9)`)
- Mehrfache Leerzeichen

**Datei:** `src/database/operations.py` → `search_items()`

### 3️⃣ Test der Lösung
Überprüft, ob die Suche jetzt funktioniert.

**Ausführen:**
```bash
test-search-fix.bat
```

## Empfohlene Reihenfolge

1. **Test vorher:** `debug-search.bat` (zeigt das Problem)
2. **Datenbank bereinigen:** `fix-nbsp.bat`
3. **Test nachher:** `test-search-fix.bat` (sollte jetzt funktionieren)
4. **Server neu starten:** `start.bat`
5. **Im Browser testen:** Suche nach "TCS-4 Undersuit Black/Grey"

## Ergebnis

Nach dem Fix sollte **"TCS-4 Undersuit Black/Grey"** gefunden werden, egal ob mit:
- ✅ normalem Leerzeichen
- ✅ non-breaking space
- ✅ mehrfachen Leerzeichen
- ✅ gemischten Leerzeichen

## Technische Details

**Non-Breaking Space (`\xa0`):**
- UTF-8 Bytes: `\xc2\xa0`
- Unicode: U+00A0
- HTML: `&nbsp;`
- Sieht aus wie ein Leerzeichen, ist aber ein anderes Zeichen!

**Warum tritt das auf?**
Websites wie CStone.space nutzen manchmal `&nbsp;` in HTML, was beim Scrapen als `\xa0` gespeichert wird.

## Scripts im Überblick

| Script | Funktion |
|--------|----------|
| `debug-search.bat` | Zeigt das Problem (Items mit \xa0) |
| `fix-nbsp.bat` | Bereinigt die Datenbank |
| `test-search-fix.bat` | Testet die verbesserte Suche |
