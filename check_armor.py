import sqlite3

conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()

# Zähle alle Items
cursor.execute('SELECT COUNT(*) FROM items')
total = cursor.fetchone()[0]
print(f'Total Items: {total}')

# Armor Items
cursor.execute("""SELECT name, item_type FROM items 
WHERE name LIKE '%Core%' 
OR name LIKE '%Arms%' 
OR name LIKE '%Legs%' 
OR name LIKE '%Helmet%' 
LIMIT 30""")

items = cursor.fetchall()

print('\n=== Armor Beispiele ===')
for name, item_type in items:
    print(f'{name} | {item_type}')

conn.close()
