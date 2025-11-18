"""
Selenium-basierter Scraper für CStone.space
Nutzt einen echten Browser um JavaScript-geladene Inhalte zu scrapen
"""
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import Database
from database.operations import ItemOperations


class SeleniumImporter:
    def __init__(self, headless=False):
        self.db = Database()
        self.operations = ItemOperations(self.db)
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"Fehler beim Starten von Chrome: {e}")
            print("\nBitte installiere ChromeDriver:")
            print("https://chromedriver.chromium.org/downloads")
            raise
        
        self.base_url = "https://finder.cstone.space"
        
        self.categories = [
            ('FPSArmors?type=Torsos', 'Torso'),
            ('FPSArmors?type=Arms', 'Arms'),
            ('FPSArmors?type=Legs', 'Legs'),
            ('FPSArmors?type=Helmets', 'Helmet'),
            ('FPSArmors?type=Backpacks', 'Backpack'),
            ('FPSArmors?type=Undersuits', 'Undersuit'),
        ]
    
    def wait_for_page_load(self, timeout=10):
        """Wartet bis die Seite vollständig geladen ist"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            # Extra Zeit für JavaScript
            time.sleep(2)
            return True
        except TimeoutException:
            print("    Timeout beim Laden der Seite")
            return False
    
    def get_items_from_category(self, category_url):
        """Extrahiert Items aus einer Kategorie"""
        try:
            url = f"{self.base_url}/{category_url}"
            print(f"  Lade: {url}")
            
            self.driver.get(url)
            self.wait_for_page_load()
            
            items = set()
            
            # Methode 1: Suche nach Links mit /FPSArmors1/
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/FPSArmors1/"]')
                for link in links:
                    text = link.text.strip()
                    if text and len(text) > 2:
                        items.add(text)
            except:
                pass
            
            # Methode 2: Suche nach Table Rows
            try:
                rows = self.driver.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    try:
                        link = row.find_element(By.TAG_NAME, 'a')
                        text = link.text.strip()
                        if text and len(text) > 2:
                            items.add(text)
                    except:
                        continue
            except:
                pass
            
            # Methode 3: Alle Links durchsuchen
            try:
                all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/FPSArmors1/' in href or '/Search/' in href:
                        text = link.text.strip()
                        if text and len(text) > 2:
                            items.add(text)
            except:
                pass
            
            print(f"    Gefunden: {len(items)} Items")
            return list(items)
        
        except Exception as e:
            print(f"    Fehler: {e}")
            return []
    
    def import_item(self, item_name, item_type):
        """Importiert ein Item"""
        try:
            existing = self.operations.get_item_by_name(item_name)
            if existing:
                return False
            
            result = self.operations.add_item(
                name=item_name,
                item_type=item_type,
                image_url=None,
                image_path=None,
                notes="Imported via Selenium"
            )
            
            return result['success']
        except Exception as e:
            print(f"    Fehler bei '{item_name}': {e}")
            return False
    
    def run(self):
        """Startet den Import"""
        print("=" * 60)
        print("CStone.space Selenium Importer")
        print("=" * 60)
        print()
        
        total_items = 0
        imported_items = 0
        
        try:
            for category_url, item_type in self.categories:
                print(f"\n📦 Kategorie: {item_type}")
                print("-" * 60)
                
                items = self.get_items_from_category(category_url)
                total_items += len(items)
                
                for i, item_name in enumerate(items, 1):
                    if self.import_item(item_name, item_type):
                        imported_items += 1
                        print(f"  [{i}/{len(items)}] ✅ {item_name}")
                    else:
                        print(f"  [{i}/{len(items)}] ⏭️  {item_name} (bereits vorhanden)")
                
                time.sleep(1)
        
        finally:
            self.driver.quit()
            self.db.close()
        
        print()
        print("=" * 60)
        print(f"Import abgeschlossen!")
        print(f"Gesamt: {total_items}")
        print(f"Neu importiert: {imported_items}")
        print("=" * 60)


if __name__ == '__main__':
    print()
    print("WICHTIG: Dieser Import nutzt Selenium und Chrome.")
    print("Chrome/ChromeDriver muss installiert sein!")
    print()
    print("Der Browser wird sich öffnen und die Seiten laden.")
    print("Das kann ein paar Minuten dauern.")
    print()
    
    response = input("Fortfahren? (j/n): ")
    
    if response.lower() in ['j', 'ja', 'y', 'yes']:
        try:
            importer = SeleniumImporter(headless=False)
            importer.run()
        except Exception as e:
            print(f"\nFehler: {e}")
            print("\nBitte installiere ChromeDriver:")
            print("1. Besuche: https://googlechromelabs.github.io/chrome-for-testing/")
            print("2. Lade chromedriver für dein System herunter")
            print("3. Entpacke es und füge es zu PATH hinzu")
            input("\nEnter drücken...")
    else:
        print("Import abgebrochen.")
