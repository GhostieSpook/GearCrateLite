"""
Fix für Non-Breaking Spaces in der Datenbank
Ersetzt alle \xa0 (non-breaking space) durch normale Leerzeichen
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'inventory.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=' * 80)
print('Bereinige Datenbank von Non-Breaking Spaces')
print('=' * 80)

# Finde alle Items mit \xa0
cursor.execute("SELECT id, name FROM items WHERE name LIKE ?", ('%\xa0%',))
items_with_nbsp = cursor.fetchall()

print(f'\nGefunden: {len(items_with_nbsp)} Items mit Non-Breaking Spaces\n')

if len(items_with_nbsp) == 0:
    print('✅ Keine Items zum Bereinigen gefunden.')
    conn.close()
    exit(0)

# Zeige Items vor der Bereinigung
for item_id, name in items_with_nbsp:
    clean_name = name.replace('\xa0', ' ')
    print(f'ID {item_id}:')
    print(f'  Vorher: {repr(name)}')
    print(f'  Nachher: {repr(clean_name)}')
    print()

# Frage Bestätigung
print('=' * 80)
response = input('Möchtest du diese Items bereinigen? (ja/nein): ')

if response.lower() not in ['ja', 'j', 'yes', 'y']:
    print('Abgebrochen.')
    conn.close()
    exit(0)

# Bereinige Items
updated_count = 0
for item_id, name in items_with_nbsp:
    clean_name = name.replace('\xa0', ' ')
    cursor.execute("UPDATE items SET name = ? WHERE id = ?", (clean_name, item_id))
    updated_count += 1

conn.commit()

print(f'\n✅ {updated_count} Items wurden bereinigt!')
print('\nÜberprüfung...')

# Überprüfung
cursor.execute("SELECT id, name FROM items WHERE name LIKE ?", ('%\xa0%',))
remaining = cursor.fetchall()

if len(remaining) == 0:
    print('✅ Alle Non-Breaking Spaces wurden entfernt!')
else:
    print(f'⚠️ Es verbleiben {len(remaining)} Items mit Non-Breaking Spaces')

conn.close()
print('\nFertig!')
