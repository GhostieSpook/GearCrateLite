import sqlite3

conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()

print("=== TORSO (Core) ===")
cursor.execute("SELECT name FROM items WHERE item_type='Torso' AND name LIKE '%ADP%' LIMIT 10")
for row in cursor.fetchall():
    print(row[0])

print("\n=== ARMS ===")
cursor.execute("SELECT name FROM items WHERE item_type='Arms' AND name LIKE '%ADP%' LIMIT 10")
for row in cursor.fetchall():
    print(row[0])

print("\n=== LEGS ===")
cursor.execute("SELECT name FROM items WHERE item_type='Legs' AND name LIKE '%ADP%' LIMIT 10")
for row in cursor.fetchall():
    print(row[0])

print("\n=== HELMET ===")
cursor.execute("SELECT name FROM items WHERE item_type='Helmet' AND (name LIKE '%Balor%' OR name LIKE '%ADP%') LIMIT 10")
for row in cursor.fetchall():
    print(row[0])

conn.close()
