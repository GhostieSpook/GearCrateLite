"""
API Backend for frontend communication – ULTRA-OPTIMIERT für Geschwindigkeit
"""
import os
import sys
import tempfile
import traceback

# Add src to path if not already there
if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Database
from database.operations import ItemOperations
from scraper.cstone import CStoneScraper
from cache.image_cache import ImageCache


class API:
    def __init__(self):
        """Initialize API with database, scraper, and cache"""
        self.db = Database()
        self.operations = ItemOperations(self.db)
        self.scraper = CStoneScraper()
        self.cache = ImageCache()

    def search_items_local(self, query):
        """Search items in local database – nur icon_url nötig"""
        if not query:
            items = self.operations.get_all_items()
        else:
            items = self.operations.search_items(query)

        for item in items:
            if item.get('image_path'):
                item['icon_url'] = self._path_to_url(item['image_path'])
            else:
                item['icon_url'] = None

        return items

    def search_items_cstone(self, query):
        """Search items on CStone.space"""
        if not query or len(query) < 2:
            return []
        return self.scraper.search_item(query)

    def add_item(self, name, item_type=None, image_url=None, notes=None, initial_count=1):
        """
        NEUE LOGIK: 
        - Item schon da → nur count +1 (kein CStone, kein Bild-Download)
        - Item neu → erst dann von CStone holen
        """
        # 1. Schon lokal vorhanden?
        existing_item = self.operations.get_item_by_name(name)
        if existing_item:
            new_count = existing_item.get('count', 0) + initial_count
            result = self.operations.update_count(name, new_count)
            if result['success']:
                item = self.operations.get_item_by_name(name)
                if item and item.get('image_path'):
                    url = self._path_to_url(item['image_path'])
                    item['icon_url'] = item['thumb_url'] = item['full_url'] = url
                return {'success': True, 'item': item, 'source': 'local'}
            return result

        # 2. Wirklich neu → von CStone holen
        if not image_url or not item_type:
            results = self.scraper.search_item(name)
            if not results:
                return {'success': False, 'error': 'Item nicht gefunden bei CStone'}

            match = next((r for r in results if r['name'].lower() == name.lower()), None)
            if not match:
                return {'success': False, 'error': 'Kein exakter Treffer'}

            item_url = match.get('url')
            if item_url:
                image_url = self.scraper.get_item_image(item_url)

        # Bild cachen (nur bei neuem Item)
        image_path = None
        if image_url:
            cached = self.cache.get_cached_path(image_url, item_type)
            if cached:
                image_path = cached
            else:
                fd, tmp = tempfile.mkstemp(suffix='.png', dir=self.cache.cache_dir)
                os.close(fd)
                try:
                    if self.scraper.download_image(image_url, tmp):
                        image_path = self.cache.save_image(image_url, tmp, item_type)
                    if os.path.exists(tmp):
                        os.remove(tmp)
                except:
                    if os.path.exists(tmp):
                        os.remove(tmp)

        result = self.operations.add_item(name, item_type, image_url, image_path, notes, initial_count)
        if result['success']:
            item = self.operations.get_item_by_name(name)
            if item and item.get('image_path'):
                url = self._path_to_url(item['image_path'])
                item['icon_url'] = item['thumb_url'] = item['full_url'] = url
            return {'success': True, 'item': item, 'source': 'cstone'}

        return result

    def get_item(self, name):
        item = self.operations.get_item_by_name(name)
        if item and item.get('image_path'):
            url = self._path_to_url(item['image_path'])
            item['icon_url'] = item['thumb_url'] = item['full_url'] = url
        return item

    def update_count(self, name, count):
        return self.operations.update_count(name, max(0, count))

    def update_notes(self, name, notes):
        return self.operations.update_notes(name, notes)

    def delete_item(self, name):
        return self.operations.delete_item(name)

    def clear_inventory(self):
        return self.operations.clear_inventory()

    def delete_all_items(self):
        return self.operations.delete_all_items()

    def clear_cache(self):
        try:
            import shutil
            for f in os.listdir(self.cache.cache_dir):
                if f != '.gitkeep':
                    fp = os.path.join(self.cache.cache_dir, f)
                    if os.path.isfile(fp):
                        os.remove(fp)
            return {'success': True, 'message': 'Cache cleared'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stats(self):
        all_items = self.operations.get_all_items()
        total_items = len(all_items)
        inventory_items = [i for i in all_items if i.get('count', 0) > 0]
        total_count = sum(i.get('count', 0) for i in all_items)
        category_counts = {}
        for i in inventory_items:
            cat = i.get('item_type', 'Unbekannt')
            category_counts[cat] = category_counts.get(cat, 0) + i.get('count', 0)

        return {
            'total_items_in_db': total_items,
            'inventory_unique_items': len(inventory_items),
            'total_item_count': total_count,
            'category_counts': category_counts,
            'cache_size_mb': round(self.cache.get_cache_size() / (1024*1024), 2)
        }

    def get_categories(self):
        items = self.operations.get_all_items()
        cats = {i.get('item_type') for i in items if i.get('item_type')}
        return sorted(cats)

    # ──────────────────────── ULTRA-SCHNELLE INVENTAR-LISTE ────────────────────────
    def get_inventory_items(self, sort_by='name', sort_order='asc', category_filter=None):
        """Nur Items mit count > 0 – direkt aus DB, keine Disk-Checks mehr"""
        try:
            query = """
                SELECT name, item_type, count, notes, image_path, added_to_inventory_at
                FROM items 
                WHERE count > 0
            """
            params = []

            if category_filter:
                query += " AND item_type = ?"
                params.append(category_filter)

            order_by = {'name': 'LOWER(name)', 'count': 'count', 'date': 'added_to_inventory_at'}.get(sort_by, 'LOWER(name)')
            query += f" ORDER BY {order_by} {'DESC' if sort_order == 'desc' else 'ASC'} NULLS LAST"

            self.db.cursor.execute(query, params)
            rows = self.db.cursor.fetchall()

            items = []
            for row in rows:
                item = dict(row)
                if item.get('image_path'):
                    url = self._path_to_url(item['image_path'])
                    item['icon_url'] = item['thumb_url'] = item['full_url'] = url
                else:
                    item['icon_url'] = item['thumb_url'] = item['full_url'] = None
                items.append(item)

            return items
        except Exception as e:
            print(f"Error get_inventory_items: {e}")
            traceback.print_exc()
            return []

    # ─────────────────────────────── URL HELPER (keine exists-Checks mehr) ──────────────────────────────
    def _path_to_url(self, file_path):
        if not file_path:
            return None
        try:
            norm = file_path.replace('\\', '/')
            marker = 'data/cache/images/'
            idx = norm.find(marker)
            if idx == -1:
                return None
            rel = norm[idx + len(marker):]
            return f'/cache/{rel}'
        except:
            return None

    # ──────────────────────── KATEGORIE-SCRAPER (unverändert) ───────────────────────
    def get_category_items(self, category_url):
        # (dein alter Code bleibt 1:1 – wird nur vom Bulk-Import benutzt)
        try:
            import urllib.parse
            from bs4 import BeautifulSoup
            import re

            category_url = urllib.parse.unquote(category_url)
            is_clothes = 'FPSClothes' in category_url
            full_url = f"https://finder.cstone.space/{category_url}"

            response = self.scraper.session.get(full_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            items = []
            rows = soup.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                name = cells[0].get_text(strip=True)
                if not name or name == 'Box':
                    continue

                link = row.find('a', href=re.compile(r'/FPS(Clothes|Armors)1/'))
                image_url = None
                if link:
                    href = link.get('href')
                    if href and not href.startswith('http'):
                        href = f"https://finder.cstone.space{href}"
                    match = re.search(r'/FPS(Clothes|Armors)1/(\d+)', href)
                    if match:
                        item_id = match.group(2)
                        image_url = f"https://cstone.space/uifimages/{item_id}.png"

                items.append({'name': name, 'url': href or None, 'image_url': image_url})

            if not items:
                type_match = re.search(r'type=([^&]+)', category_url)
                if type_match:
                    item_type = type_match.group(1)
                    ajax_url = f"https://finder.cstone.space/Get{'Clothes' if is_clothes else 'Armors'}/{item_type}"
                    ajax = self.scraper.session.get(ajax_url, timeout=15)
                    ajax.raise_for_status()
                    for it in ajax.json():
                        iid = it.get('ItemId')
                        iname = it.get('Name')
                        if iid and iname:
                            detail = f"https://finder.cstone.space/FPS{'Clothes' if is_clothes else 'Armors'}1/{iid}"
                            items.append({'name': iname, 'url': detail, 'image_url': f"https://cstone.space/uifimages/{iid}.png"})

            return items
        except Exception as e:
            print(f"Error get_category_items: {e}")
            traceback.print_exc()
            return []

    def close(self):
        self.db.close()