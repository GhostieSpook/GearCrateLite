"""
Debug-Script zur Diagnose des Suchproblems mit TCS-4 Undersuit
Führe dieses Script mit: python debug_search.py
"""
import sqlite3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Verbindung zur Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'data', 'inventory.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Suche nach TCS-4 Items
cursor.execute("SELECT name FROM items WHERE name LIKE '%TCS-4%'")
items = cursor.fetchall()

print('=' * 80)
print('Items mit "TCS-4" im Namen:')
print('=' * 80)
for item in items:
    name = item["name"]
    print(f'  Name: "{name}"')
    print(f'    Länge: {len(name)} Zeichen')
    print(f'    Repr: {repr(name)}')
    print(f'    Bytes: {name.encode("utf-8")}')
    # Zeige versteckte Zeichen
    visible = ''.join(c if c.isprintable() else f'\\x{ord(c):02x}' for c in name)
    print(f'    Sichtbar: {visible}')
    print()

# Test verschiedene Suchqueries
test_queries = [
    'TCS-4 Undersuit',
    'TCS-4 Undersuit ',  # Mit Leerzeichen am Ende
    'TCS-4 Undersuit Black/Grey',
    'TCS-4 Undersuit B',
    'Black/Grey',
    'Undersuit Black',
]

print('=' * 80)
print('Test verschiedener Suchqueries (direkt in DB):')
print('=' * 80)
for query in test_queries:
    cursor.execute('SELECT name FROM items WHERE name LIKE ?', (f'%{query}%',))
    results = cursor.fetchall()
    print(f'Query: "{query}" (Länge: {len(query)})')
    print(f'  -> {len(results)} Ergebnis(se)')
    if len(results) > 0:
        for r in results:
            print(f'    ✓ "{r["name"]}"')
    else:
        print(f'    ✗ Keine Ergebnisse')
    print()

# Test mit trim() simulieren (wie in app.js)
print('=' * 80)
print('Test mit .strip() (simuliert JavaScript .trim()):')
print('=' * 80)
test_queries_trimmed = [
    'TCS-4 Undersuit Black/Grey',
    '  TCS-4 Undersuit Black/Grey  ',
]
for query in test_queries_trimmed:
    trimmed = query.strip()
    cursor.execute('SELECT name FROM items WHERE name LIKE ?', (f'%{trimmed}%',))
    results = cursor.fetchall()
    print(f'Original: "{query}"')
    print(f'Trimmed:  "{trimmed}"')
    print(f'  -> {len(results)} Ergebnis(se)')
    if len(results) > 0:
        for r in results:
            print(f'    ✓ "{r["name"]}"')
    else:
        print(f'    ✗ Keine Ergebnisse')
    print()

conn.close()
print('Test abgeschlossen!')
