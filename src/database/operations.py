"""
Database operations (CRUD) for inventory items
"""
from datetime import datetime


class ItemOperations:
    def __init__(self, database):
        """Initialize with database instance"""
        self.db = database
    
    def add_item(self, name, item_type=None, image_url=None, image_path=None, notes=None, initial_count=1):
        """Add a new item or increment count if exists
        
        Args:
            initial_count: Starting count for new items (default 1, use 0 for imports)
        """
        try:
            # Check if item already exists
            existing = self.get_item_by_name(name)
            
            if existing:
                # Item exists - only increment if initial_count > 0
                if initial_count > 0:
                    new_count = existing['count'] + initial_count
                    
                    # Setze added_to_inventory_at, wenn Item von 0 zu >0 wechselt
                    if existing['count'] == 0 and new_count > 0:
                        self.db.cursor.execute('''
                            UPDATE items 
                            SET count = ?, updated_at = ?, added_to_inventory_at = ?
                            WHERE name = ?
                        ''', (new_count, datetime.now(), datetime.now(), name))
                    else:
                        self.db.cursor.execute('''
                            UPDATE items 
                            SET count = ?, updated_at = ? 
                            WHERE name = ?
                        ''', (new_count, datetime.now(), name))
                    
                    self.db.conn.commit()
                    return {'success': True, 'count': new_count, 'new': False}
                else:
                    # Item exists and initial_count is 0 - do nothing
                    return {'success': True, 'count': existing['count'], 'new': False, 'skipped': True}
            else:
                # Insert new item with initial_count
                # Setze added_to_inventory_at NUR wenn initial_count > 0
                if initial_count > 0:
                    self.db.cursor.execute('''
                        INSERT INTO items (name, item_type, image_url, image_path, notes, count, added_to_inventory_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, item_type, image_url, image_path, notes, initial_count, datetime.now()))
                else:
                    # Bulk-Import: KEIN added_to_inventory_at setzen
                    self.db.cursor.execute('''
                        INSERT INTO items (name, item_type, image_url, image_path, notes, count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, item_type, image_url, image_path, notes, initial_count))
                
                self.db.conn.commit()
                return {'success': True, 'count': initial_count, 'new': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_item_by_name(self, name):
        """Get item by exact name"""
        self.db.cursor.execute('SELECT * FROM items WHERE name = ?', (name,))
        row = self.db.cursor.fetchone()
        return dict(row) if row else None
    
    def search_items(self, query):
        """Search items by name (case-insensitive, partial match)
        
        Normalisiert verschiedene Leerzeichen-Arten für bessere Suche:
        - Non-breaking spaces (\xa0 / CHAR(160))
        - Tabs (CHAR(9))
        - Mehrfache Leerzeichen
        """
        import re
        
        # Normalisiere Leerzeichen im Suchstring
        # Ersetzt: non-breaking space, tab, mehrfache Leerzeichen, etc.
        query_normalized = re.sub(r'\s+', ' ', query.strip())
        
        # Suche mit LIKE - REPLACE normalisiert verschiedene Leerzeichen in der DB
        # CHAR(160) = non-breaking space (\xa0)
        # CHAR(9) = tab
        self.db.cursor.execute('''
            SELECT * FROM items 
            WHERE REPLACE(REPLACE(name, CHAR(160), ' '), CHAR(9), ' ') LIKE ? 
            ORDER BY name
        ''', (f'%{query_normalized}%',))
        rows = self.db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_items(self):
        """Get all items"""
        self.db.cursor.execute('SELECT * FROM items ORDER BY name')
        rows = self.db.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_count(self, name, count):
        """Update item count"""
        try:
            # Hole aktuellen count um zu prüfen ob von 0 zu >0
            existing = self.get_item_by_name(name)
            
            if existing and existing['count'] == 0 and count > 0:
                # Von 0 zu >0: Setze added_to_inventory_at
                self.db.cursor.execute('''
                    UPDATE items 
                    SET count = ?, updated_at = ?, added_to_inventory_at = ?
                    WHERE name = ?
                ''', (count, datetime.now(), datetime.now(), name))
            else:
                # Normal update ohne added_to_inventory_at
                self.db.cursor.execute('''
                    UPDATE items 
                    SET count = ?, updated_at = ? 
                    WHERE name = ?
                ''', (count, datetime.now(), name))
            
            self.db.conn.commit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_notes(self, name, notes):
        """Update item notes"""
        try:
            self.db.cursor.execute('''
                UPDATE items 
                SET notes = ?, updated_at = ? 
                WHERE name = ?
            ''', (notes, datetime.now(), name))
            self.db.conn.commit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_item(self, name):
        """Delete an item"""
        try:
            self.db.cursor.execute('DELETE FROM items WHERE name = ?', (name,))
            self.db.conn.commit()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_inventory(self):
        """Set all item counts to 0 (empty inventory but keep items in database)"""
        try:
            self.db.cursor.execute('UPDATE items SET count = 0')
            self.db.conn.commit()
            affected = self.db.cursor.rowcount
            return {'success': True, 'affected': affected}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_all_items(self):
        """Delete ALL items from database"""
        try:
            self.db.cursor.execute('DELETE FROM items')
            self.db.conn.commit()
            affected = self.db.cursor.rowcount
            return {'success': True, 'deleted': affected}
        except Exception as e:
            return {'success': False, 'error': str(e)}
