"""
CStone.space Bulk Importer
Holt alle FPS-Rüstungsteile von CStone und importiert sie in die Datenbank
"""
import sys
import os
import time
import requests
from bs4 import BeautifulSoup
import re

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import Database
from database.operations import ItemOperations
from scraper.cstone import CStoneScraper
from cache.image_cache import ImageCache


class BulkImporter:
    def __init__(self):
        self.db = Database()
        self.operations = ItemOperations(self.db)
        self.scraper = CStoneScraper()
        self.cache = ImageCache()
        
        self.base_url = "https://finder.cstone.space"
        self.categories = [
            ('FPSArmors?type=Torsos', 'Torso'),
            ('FPSArmors?type=Arms', 'Arms'),
            ('FPSArmors?type=Legs', 'Legs'),
            ('FPSArmors?type=Helmets', 'Helmet'),
            ('FPSArmors?type=Backpacks', 'Backpack'),
            ('FPSArmors?type=Undersuits', 'Undersuit'),
        ]
    
    def get_all_items_from_category(self, category_url):
        """Holt alle Items aus einer Kategorie"""
        try:
            url = f"{self.base_url}/{category_url}"
            print(f"  Lade: {url}")
            
            response = self.scraper.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = []
            
            # Suche nach Item-Links
            # CStone hat verschiedene Strukturen, versuche mehrere Selektoren
            
            # Methode 1: Links zu FPSArmors1
            links = soup.find_all('a', href=re.compile(r'/FPSArmors1/'))
            for link in links:
                item_name = link.get_text(strip=True)
                item_url = link.get('href')
                
                if item_name and item_url:
                    if not item_url.startswith('http'):
                        item_url = f"{self.base_url}{item_url}"
                    
                    items.append({
                        'name': item_name,
                        'url': item_url
                    })
            
            # Methode 2: Table rows
            if not items:
                rows = soup.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        link = row.find('a')
                        if link:
                            item_name = link.get_text(strip=True)
                            item_url = link.get('href')
                            
                            if item_name and item_url:
                                if not item_url.startswith('http'):
                                    item_url = f"{self.base_url}{item_url}"
                                
                                items.append({
                                    'name': item_name,
                                    'url': item_url
                                })
            
            print(f"    Gefunden: {len(items)} Items")
            return items
        
        except Exception as e:
            print(f"    Fehler beim Laden der Kategorie: {e}")
            return []
    
    def import_item(self, item_name, item_type, item_url):
        """Importiert ein einzelnes Item"""
        try:
            # Check if already exists
            existing = self.operations.get_item_by_name(item_name)
            if existing:
                print(f"    ⏭️  '{item_name}' bereits vorhanden")
                return True
            
            # Get image
            image_url = self.scraper.get_item_image(item_url)
            image_path = None
            
            if image_url:
                # Check cache
                cached = self.cache.get_cached_path(image_url)
                if cached:
                    image_path = cached
                else:
                    # Download
                    temp_path = os.path.join(self.cache.cache_dir, 'temp_bulk.jpg')
                    if self.scraper.download_image(image_url, temp_path):
                        image_path = self.cache.save_image(image_url, temp_path)
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            
            # Add to database
            result = self.operations.add_item(
                name=item_name,
                item_type=item_type,
                image_url=image_url,
                image_path=image_path,
                notes=None
            )
            
            if result['success']:
                print(f"    ✅ '{item_name}' importiert")
                return True
            else:
                print(f"    ❌ Fehler bei '{item_name}': {result.get('error')}")
                return False
        
        except Exception as e:
            print(f"    ❌ Fehler bei '{item_name}': {e}")
            return False
    
    def run(self):
        """Startet den Bulk-Import"""
        print("=" * 60)
        print("CStone.space Bulk Importer")
        print("=" * 60)
        print()
        
        total_items = 0
        imported_items = 0
        
        for category_url, item_type in self.categories:
            print(f"\n📦 Kategorie: {item_type}")
            print("-" * 60)
            
            items = self.get_all_items_from_category(category_url)
            total_items += len(items)
            
            for i, item in enumerate(items, 1):
                print(f"  [{i}/{len(items)}] {item['name']}")
                
                if self.import_item(item['name'], item_type, item['url']):
                    imported_items += 1
                
                # Rate limiting
                time.sleep(0.5)
        
        print()
        print("=" * 60)
        print(f"Import abgeschlossen!")
        print(f"Gesamt gefunden: {total_items}")
        print(f"Importiert: {imported_items}")
        print("=" * 60)
        
        self.db.close()


if __name__ == '__main__':
    print()
    print("WARNUNG: Dieser Import kann mehrere Minuten dauern!")
    print("Es werden hunderte Items von CStone.space geladen.")
    print()
    
    response = input("Fortfahren? (j/n): ")
    
    if response.lower() in ['j', 'ja', 'y', 'yes']:
        importer = BulkImporter()
        importer.run()
    else:
        print("Import abgebrochen.")
