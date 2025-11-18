"""
Test-Script um zu überprüfen, ob die Suche jetzt funktioniert
Testet die Suche NACH dem Fix der Suchfunktion
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.models import Database
from database.operations import ItemOperations

# Initialize
db = Database()
ops = ItemOperations(db)

print('=' * 80)
print('Test der verbesserten Suchfunktion')
print('=' * 80)

# Test-Queries
test_queries = [
    'TCS-4 Undersuit',
    'TCS-4 Undersuit Black/Grey',
    'TCS-4 Undersuit B',
    'Black/Grey',
]

print('\nSuche mit der verbesserten search_items() Funktion:\n')

for query in test_queries:
    results = ops.search_items(query)
    print(f'Query: "{query}"')
    print(f'  -> {len(results)} Ergebnis(se)')
    if len(results) > 0:
        for item in results:
            if 'TCS-4' in item['name']:
                print(f'    ✓ "{item["name"]}"')
    else:
        print(f'    ✗ Keine Ergebnisse')
    print()

# Spezifischer Test für TCS-4 Undersuit Black/Grey
print('=' * 80)
print('Spezifischer Test: "TCS-4 Undersuit Black/Grey"')
print('=' * 80)
results = ops.search_items('TCS-4 Undersuit Black/Grey')
if len(results) > 0:
    print(f'\n✅ ERFOLG! Gefunden: {len(results)} Ergebnis(se)')
    for item in results:
        print(f'  - {item["name"]}')
else:
    print('\n❌ FEHLER! Keine Ergebnisse gefunden.')
    print('Möglicherweise musst du erst die Datenbank bereinigen (fix-nbsp.bat)')

db.close()
print('\n' + '=' * 80)
print('Test abgeschlossen!')
print('=' * 80)
