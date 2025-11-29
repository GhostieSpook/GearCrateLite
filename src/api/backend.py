"""
API Backend for frontend communication
"""
import os
import sys
import json
import tempfile
from urllib.parse import urlparse, parse_qs

# Add src to path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from database.models import Database
from database.operations import ItemOperations
from scraper.cstone import CStoneScraper
from cache.image_cache import ImageCache
from cache.gear_sets import GearSetsManager


class API:
    # Class variable to store pywebview window reference
    _webview_window = None

    def __init__(self):
        """Initialize API with database, scraper, and cache"""
        self.db = Database()
        self.operations = ItemOperations(self.db)
        self.scraper = CStoneScraper()
        self.cache = ImageCache()
        self.gear_sets = GearSetsManager()

    @classmethod
    def set_webview_window(cls, window):
        """Set the pywebview window reference (called from main_desktop.py)"""
        cls._webview_window = window

    def _path_to_url(self, path):
        """
        Converts an absolute cache path (containing category subfolders) 
        to a relative URL path usable by the browser server (starting with /cache/).
        (FIXED for subfolders)
        """
        if not path:
            return None
            
        # 1. Normalisieren des Pfadtrenners für URL
        path = path.replace('\\', '/')
        
        # 2. Den Teil ab 'data/images/' finden und durch '/images/' ersetzen
        search_string = 'data/images/'
        if search_string in path:
            parts = path.split(search_string)
            if len(parts) > 1:
                return f"/images/{parts[1]}"

        # Fallback
        return path

    def search_items_local(self, query):
        """
        Search items in local database (for the Search Tab).
        CRITICAL: This must return ALL items (count >= 0) to allow searching for items not yet in inventory.
        """
        # Wir verwenden search_items mit include_zero_count=True (Standard in operations.py)
        if not query:
            items = self.operations.get_all_items(include_zero_count=True)
        else:
            items = self.operations.search_items(query, include_zero_count=True)

        # Daten für Frontend aufbereiten
        for item in items:
            item['is_favorite'] = bool(item.get('is_favorite', 0))
            if item.get('image_path'):
                item['icon_url'] = self._path_to_url(item['image_path'])
            else:
                item['icon_url'] = item.get('image_url')

        return items

    def search_items_cstone(self, query):
        """Search items on CStone.space"""
        if not query or len(query) < 2:
            return []
        return self.scraper.search_item(query)

    def add_item(self, name, item_type=None, image_url=None, notes=None, initial_count=1, properties_json=None):
        """Adds an item to the inventory"""

        # 1. Details und Properties scrapen, wenn URL fehlt
        if not image_url:
            print(f"INFO: No image_url provided for {name}, attempting to scrape full details...")
            full_details = self.scraper.get_item_details(name)
            if full_details:
                image_url = full_details.get('image_url')
                # Wenn wir scraped properties haben, nutzen wir diese
                if full_details.get('properties'):
                    properties_json = json.dumps(full_details.get('properties', {}))

        # 2. Bild herunterladen und cachen
        image_path = None
        if image_url:
            # Check if already cached
            cached_path = self.cache.get_cached_path(image_url, item_type)
            if cached_path:
                image_path = cached_path
            else:
                # Download image to temporary file first
                import tempfile
                import requests
                import os as os_lib
                try:
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                            tmp_file.write(response.content)
                            tmp_path = tmp_file.name

                        # Save to cache (this also generates thumbnails)
                        image_path = self.cache.save_image(image_url, tmp_path, item_type)

                        # Clean up temp file
                        try:
                            os_lib.remove(tmp_path)
                        except:
                            pass
                except Exception as e:
                    print(f"Error downloading image for {name}: {e}")

        # 3. In DB speichern (ohne properties_json wenn die Spalte nicht existiert)
        try:
            result = self.operations.add_item(name, item_type, image_url, image_path, notes, initial_count, properties_json)
        except Exception as e:
            # Falls properties_json Spalte nicht existiert, versuche ohne
            if 'properties_json' in str(e):
                result = self.operations.add_item(name, item_type, image_url, image_path, notes, initial_count)
            else:
                raise e

        return result

    def update_item_count(self, name, count):
        """Update the count of an existing item"""
        return self.operations.update_item_count(name, count)
        
    def update_count(self, name, count):
        """Alias for update_item_count (used by some frontend quick actions)"""
        return self.update_item_count(name, count)
        
    def update_item_notes(self, name, notes):
        """Update item notes"""
        return self.operations.update_item_notes(name, notes)

    def delete_item(self, name):
        """Delete an item (removes from DB)"""
        return self.operations.delete_item(name)
    
    def delete_all_items(self):
        """Delete ALL items"""
        return self.operations.delete_all_items()

    def get_item(self, name):
        """Retrieve full details for an item from local DB (used by app.js)"""
        item = self.operations.get_item_by_name(name)
        if item:
            item['is_favorite'] = bool(item.get('is_favorite', 0))
            if item.get('image_path'):
                # URLs für verschiedene Zwecke setzen
                url = self._path_to_url(item['image_path'])
                item['full_image_url'] = url
                item['icon_url'] = url
                item['thumb_url'] = url
            else:
                url = item.get('image_url')
                item['full_image_url'] = url
                item['icon_url'] = url
                item['thumb_url'] = url
        return item
        
    def get_categories(self):
        """Retrieve all distinct item types for filters"""
        stats = self.get_category_stats()
        # 'Favorites' aus der Liste der normalen Kategorien filtern
        types = [t for t in stats.get('category_counts', {}).keys() if t != 'Favorites']
        return sorted(types)

    def get_category_stats(self):
        """Get inventory stats by item category"""
        stats = self.operations.get_category_stats()
        return {'category_counts': stats}
        
    def get_stats(self):
        """Get general stats"""
        # include_zero_count=True um alle Items in DB zu zählen
        all_items_db = self.operations.get_all_items(include_zero_count=True)
        all_items_inventory = self.operations.get_all_items(include_zero_count=False)
        
        total_count = sum(item['count'] for item in all_items_inventory)
        unique_items = len(all_items_inventory)
        total_db = len(all_items_db)
        
        # Cache size berechnen
        cache_size = 0
        cache_dir = os.path.join('data', 'cache', 'images')
        if os.path.exists(cache_dir):
            for root, _, files in os.walk(cache_dir):
                for f in files:
                    cache_size += os.path.getsize(os.path.join(root, f))
        
        return {
            'total_items_in_db': total_db,
            'inventory_unique_items': unique_items,
            'total_item_count': total_count,
            'cache_size_mb': round(cache_size / (1024 * 1024), 2),
            'category_counts': self.operations.get_category_stats()
        }

    def clear_inventory(self):
        """
        Set all item counts to 0 (empty inventory but keep items in database).
        """
        return self.operations.clear_inventory()

    def clear_cache(self):
        """Clear the image cache"""
        success = self.cache.clear_cache()
        if success:
            return {'success': True, 'message': 'Cache erfolgreich geleert'}
        else:
            return {'success': False, 'error': 'Fehler beim Leeren des Cache'}

    # =========================================================
    # HAUPTFUNKTIONEN FÜR INVENTAR & FAVORITEN
    # =========================================================

    def inventory(self, sort_by='name', sort_order='asc', query='', category=None, is_favorite=None):
        """
        Retrieves the filtered and sorted inventory list.
        Handler für /api/get_inventory_items
        CRITICAL: This must only show items with count > 0.
        """
        
        # 1. Daten aus DB holen (wir verwenden IMMER include_zero_count=False für Inventar-Ansichten)
        filter_favorite = 1 if str(is_favorite).lower() in ('1', 'true') else None
        
        if query:
            # Suche INNERHALB des Inventars (Count > 0)
            items = self.operations.search_items(query, include_zero_count=False)
        else:
            # Normale Listenansicht (Count > 0, optional Favorite Filter)
            items = self.operations.get_all_items(is_favorite=filter_favorite, include_zero_count=False)

        # 2. Kategorie-Filter anwenden (wenn nicht Favorites, da das schon oben passiert ist)
        if category and category != 'Favorites' and category != '':
             items = [item for item in items if item.get('item_type') == category]

        # 3. Daten aufbereiten (URLs & is_favorite Boolean)
        processed_items = []
        for item in items:
            # Das manuelle Count-Filter ist jetzt überflüssig, da die DB-Abfrage dies übernimmt!
            
            # Konvertiere für JSON
            item_dict = dict(item)
            item_dict['is_favorite'] = bool(item_dict.get('is_favorite', 0))
            
            if item_dict.get('image_path'):
                item_dict['thumb_url'] = self._path_to_url(item_dict['image_path'])
                item_dict['icon_url'] = item_dict['thumb_url']
            else:
                item_dict['thumb_url'] = item_dict.get('image_url')
                item_dict['icon_url'] = item_dict.get('image_url')
                
            processed_items.append(item_dict)

        # 4. Sortierung (Python-seitig, da wir hier flexibler sind)
        reverse_sort = (sort_order.lower() == 'desc')
        
        def sort_key(x):
            key = sort_by
            # FIX: Mapping von 'date' auf die korrekte DB-Spalte
            if key == 'date':
                key = 'added_to_inventory_at'
            
            val = x.get(key)
            if val is None:
                # Leere Werte (z.B. wenn added_to_inventory_at noch NULL ist) am Ende sortieren
                return ''
            if isinstance(val, str):
                return val.lower()
            return val

        try:
            processed_items.sort(key=sort_key, reverse=reverse_sort)
        except Exception:
            # Fallback auf Name, falls Sortierung fehlschlägt
            processed_items.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse_sort)
            
        return processed_items

    def toggle_favorite(self, name, is_favorite):
        """
        Toggles the favorite status of an item.
        """
        try:
            # Sicherstellen, dass wir einen Integer (0 oder 1) haben
            if isinstance(is_favorite, str):
                status_val = 1 if is_favorite.lower() in ('1', 'true', 'yes') else 0
            else:
                status_val = 1 if is_favorite else 0
                
            return self.operations.toggle_favorite_status(name, status_val)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # =========================================================
    # GEAR SETS FUNKTIONEN
    # =========================================================

    def get_all_gear_sets(self):
        """
        Gibt eine Liste aller verfügbaren Gear Sets zurück.
        Jedes Set enthält: Name, Anzahl Varianten, Beispiel-Varianten
        """
        try:
            summary = self.gear_sets.get_all_sets_summary(self.db.conn)
            return {'success': True, 'sets': summary}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_gear_set_details(self, set_name, variant=''):
        """
        Gibt Details zu einem spezifischen Set zurück.
        Enthält alle 4 Teile mit Bildern und Inventar-Status.
        """
        try:
            pieces = self.gear_sets.get_set_pieces(self.db.conn, set_name, variant)
            
            if not pieces:
                return {'success': False, 'error': 'Set nicht gefunden'}
            
            # Bereite Daten für Frontend auf
            result = {
                'set_name': set_name,
                'variant': variant if variant else 'Base',
                'pieces': {}
            }
            
            # Zähle wie viele Teile vorhanden sind
            owned_count = 0
            
            for part_type, piece in pieces.items():
                if piece:
                    # Teil existiert in DB
                    piece_data = {
                        'exists': True,
                        'name': piece['name'],
                        'count': piece.get('count', 0),
                        'owned': piece.get('count', 0) > 0,
                        'image_url': None
                    }
                    
                    # Bild-URL hinzufügen
                    if piece.get('image_path'):
                        piece_data['image_url'] = self._path_to_url(piece['image_path'])
                    elif piece.get('image_url'):
                        piece_data['image_url'] = piece['image_url']
                    
                    if piece_data['owned']:
                        owned_count += 1
                    
                    result['pieces'][part_type] = piece_data
                else:
                    # Teil nicht in DB gefunden
                    result['pieces'][part_type] = {
                        'exists': False,
                        'name': None,
                        'count': 0,
                        'owned': False,
                        'image_url': None
                    }
            
            result['owned_count'] = owned_count
            result['total_count'] = 4
            result['completion'] = f"{owned_count}/4"
            
            return {'success': True, 'set': result}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_gear_set_variants(self, set_name):
        """
        Gibt alle Farbvarianten eines Sets zurück.
        """
        try:
            variants = self.gear_sets.get_set_variants(self.db.conn, set_name)
            return {'success': True, 'variants': variants}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # =========================================================
    # BULK IMPORT FUNKTIONEN
    # =========================================================

    def get_category_items(self, category_url):
        """
        Holt alle Items einer Kategorie von CStone.space
        category_url: z.B. 'FPSArmors?type=Torsos' oder 'FPSClothes?type=Hat'
        Returns: List of items with name and image_url
        """
        try:
            items = self.scraper.get_category_items(category_url)
            return items
        except Exception as e:
            print(f"Error in get_category_items: {e}")
            import traceback
            traceback.print_exc()
            raise e

    # =========================================================
    # INVENTORY SCANNER FUNKTIONEN
    # =========================================================

    def set_scan_mode(self, mode):
        """
        Sets the scan mode in InvDetect/config.py
        mode: 1 (1x1) or 2 (1x2)
        """
        import os

        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'InvDetect', 'config.py')

        try:
            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Update SCAN_MODE line
            for i, line in enumerate(lines):
                if line.strip().startswith('SCAN_MODE ='):
                    lines[i] = f'SCAN_MODE = {mode}\n'
                    break

            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return {'success': True, 'mode': mode}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start_scanner(self):
        """
        Starts the InvDetect scanner as a subprocess (CMD window)
        """
        import subprocess
        import os

        # Path to InvDetect main.py
        invdetect_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'InvDetect')
        main_py = os.path.join(invdetect_dir, 'main.py')

        try:
            # Start as CMD window (visible for debugging)
            # Using 'start' command to open new CMD window
            # /c closes window after script completes
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/c', 'python', main_py],
                cwd=invdetect_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            return {'success': True, 'message': 'Scanner started'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_scan_results(self):
        """
        Reads detected_items.txt and not_detected.md, matches items with database
        Returns: {found: [...], not_found: [...]}
        """
        import os
        from rapidfuzz import fuzz, process

        invdetect_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'InvDetect')
        detected_file = os.path.join(invdetect_dir, 'detected_items.txt')
        not_detected_file = os.path.join(invdetect_dir, 'not_detected.md')

        found_items = []
        not_found_items = []

        # Read detected_items.txt
        if os.path.exists(detected_file):
            try:
                with open(detected_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue

                        # Format: "count, item_name"
                        parts = line.split(',', 1)
                        if len(parts) == 2:
                            count = int(parts[0].strip())
                            item_name = parts[1].strip()

                            # Fuzzy match with database
                            all_items = self.operations.get_all_items(include_zero_count=True)
                            item_names = [item['name'] for item in all_items]

                            match = process.extractOne(item_name, item_names, scorer=fuzz.ratio)

                            if match and match[1] >= 75:  # 75% match threshold
                                matched_name = match[0]
                                db_item = next((item for item in all_items if item['name'] == matched_name), None)

                                if db_item:
                                    found_items.append({
                                        'name': db_item['name'],
                                        'scanned_name': item_name,
                                        'count': count,
                                        'item_type': db_item.get('item_type'),
                                        'image_url': self._path_to_url(db_item.get('image_path')) if db_item.get('image_path') else db_item.get('image_url'),
                                        'db_id': db_item.get('id')
                                    })
            except Exception as e:
                print(f"Error reading detected_items.txt: {e}")

        # Read not_detected.md
        if os.path.exists(not_detected_file):
            try:
                with open(not_detected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse file - accept lines with or without '-' prefix
                    for line in content.split('\n'):
                        line = line.strip()
                        # Skip empty lines, comments, and header separators
                        if not line or line.startswith('#') or line.startswith('---'):
                            continue

                        # Remove optional '- ' prefix if present
                        if line.startswith('-'):
                            text = line.lstrip('- ').strip()
                        else:
                            text = line

                        if text:
                            not_found_items.append({'ocr_text': text})
            except Exception as e:
                print(f"Error reading not_detected.md: {e}")

        return {
            'success': True,
            'found': found_items,
            'not_found': not_found_items
        }

    def import_scanned_items(self, items):
        """
        Imports scanned items into inventory
        items: [{name, count}, ...]
        For existing items: adds to count
        For new items: creates with scanned count
        """
        import_results = []

        for item_data in items:
            item_name = item_data.get('name')
            scanned_count = item_data.get('count', 1)

            try:
                # Check if item exists
                existing = self.operations.get_item(item_name)

                if existing:
                    # Item exists → add to count
                    new_count = existing.get('count', 0) + scanned_count
                    result = self.operations.update_item_count(item_name, new_count)
                    import_results.append({
                        'name': item_name,
                        'action': 'updated',
                        'old_count': existing.get('count', 0),
                        'new_count': new_count,
                        'success': result.get('success', False)
                    })
                else:
                    # Item doesn't exist → should not happen (items come from DB)
                    # But just in case, we create it
                    result = self.operations.update_item_count(item_name, scanned_count)
                    import_results.append({
                        'name': item_name,
                        'action': 'created',
                        'count': scanned_count,
                        'success': result.get('success', False)
                    })

            except Exception as e:
                import_results.append({
                    'name': item_name,
                    'action': 'error',
                    'error': str(e),
                    'success': False
                })

        return {
            'success': True,
            'results': import_results
        }

    def open_not_detected_file(self):
        """
        Opens the not_detected.md file in file explorer and highlights it
        """
        import os
        import subprocess
        import platform

        # Get InvDetect directory
        invdetect_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'InvDetect'
        )
        not_detected_file = os.path.join(invdetect_dir, 'not_detected.md')

        if not os.path.exists(not_detected_file):
            return {'success': False, 'error': 'not_detected.md nicht gefunden'}

        try:
            # Windows: Use explorer /select to highlight the file
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', '/select,', os.path.normpath(not_detected_file)])
            # macOS: Use Finder
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', '-R', not_detected_file])
            # Linux: Open containing folder
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(not_detected_file)])

            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def open_devtools(self):
        """
        Opens/Toggles DevTools in Desktop mode (pywebview)
        Uses pyautogui to simulate F12 keypress
        """
        try:
            # Simulate F12 keypress to toggle DevTools
            import pyautogui
            import threading

            def toggle():
                pyautogui.press('f12')

            # Run in thread to not block
            threading.Thread(target=toggle, daemon=True).start()
            return {'success': True}
        except ImportError:
            return {'success': False, 'error': 'pyautogui nicht verfügbar'}
        except Exception as e:
            return {'success': False, 'error': str(e)}