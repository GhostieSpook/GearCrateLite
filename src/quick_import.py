"""
Schneller Import - nur Item-Namen, keine Bilder
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


class QuickImporter:
    def __init__(self):
        self.db = Database()
        self.operations = ItemOperations(self.db)
        
        self.base_url = "https://finder.cstone.space"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.categories = [
            ('FPSArmors?type=Torsos', 'Torso'),
            ('FPSArmors?type=Arms', 'Arms'),
            ('FPSArmors?type=Legs', 'Legs'),
            ('FPSArmors?type=Helmets', 'Helmet'),
            ('FPSArmors?type=Backpacks', 'Backpack'),
            ('FPSArmors?type=Undersuits', 'Undersuit'),
        ]
    
    def get_all_item_names(self, category_url):
        """Holt nur die Item-Namen aus einer Kategorie"""
        try:
            url = f"{self.base_url}/{category_url}"
            print(f"  Lade: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = set()
            
            # Suche nach Item-Links
            links = soup.find_all('a', href=re.compile(r'/FPSArmors1/|/Search/'))
            for link in links:
                item_name = link.get_text(strip=True)
                if item_name and len(item_name) > 2:
                    items.add(item_name)
            
            # Table rows
            rows = soup.find_all('tr')
            for row in rows[1:]:
                link = row.find('a')
                if link:
                    item_name = link.get_text(strip=True)
                    if item_name and len(item_name) > 2:
                        items.add(item_name)
            
            print(f"    Gefunden: {len(items)} Items")
            return list(items)
        
        except Exception as e:
            print(f"    Fehler: {e}")
            return []
    
    def import_item_quick(self, item_name, item_type):
        """Schneller Import ohne Bilder"""
        try:
            existing = self.operations.get_item_by_name(item_name)
            if existing:
                return False
            
            result = self.operations.add_item(
                name=item_name,
                item_type=item_type,
                image_url=None,
                image_path=None,
                notes="Imported from CStone (no image)"
            )
            
            return result['success']
        
        except Exception as e:
            print(f"    Fehler bei '{item_name}': {e}")
            return False
    
    def run(self):
        """Startet den Quick-Import"""
        print("=" * 60)
        print("CStone.space Quick Import (nur Namen)")
        print("=" * 60)
        print()
        
        total_items = 0
        imported_items = 0
        
        for category_url, item_type in self.categories:
            print(f"\n📦 Kategorie: {item_type}")
            print("-" * 60)
            
            items = self.get_all_item_names(category_url)
            total_items += len(items)
            
            for item_name in items:
                if self.import_item_quick(item_name, item_type):
                    imported_items += 1
                    print(f"    ✅ {item_name}")
            
            time.sleep(1)
        
        print()
        print("=" * 60)
        print(f"Quick-Import abgeschlossen!")
        print(f"Gesamt: {total_items}")
        print(f"Neu importiert: {imported_items}")
        print("=" * 60)
        print()
        print("Tipp: Du kannst später Bilder für einzelne Items")
        print("      über die normale Suche hinzufügen.")
        
        self.db.close()


if __name__ == '__main__':
    print()
    print("Dies ist ein SCHNELLER Import ohne Bilder.")
    print("Die Bilder können später über die normale Suche hinzugefügt werden.")
    print()
    
    response = input("Fortfahren? (j/n): ")
    
    if response.lower() in ['j', 'ja', 'y', 'yes']:
        importer = QuickImporter()
        importer.run()
    else:
        print("Import abgebrochen.")
