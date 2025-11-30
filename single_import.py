"""
Single Import - Importiert einzelne Items von Star Citizen Wiki URLs
"""
import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import tempfile
from PIL import Image

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.backend import API


def extract_item_type_from_classname(classname):
    """
    Extrahiert den item_type aus dem Klassennamen.
    Beispiel: 'cds_legacy_armor_heavy_core_01_01_01' → 'Torso'
    """
    if not classname:
        return None

    classname_lower = classname.lower()

    # Mapping von Klassenname-Keywords zu item_type
    type_mapping = {
        'helmet': 'Helmet',
        'core': 'Torso',
        'torso': 'Torso',
        'arms': 'Arms',
        'legs': 'Legs',
        'backpack': 'Backpack',
        'undersuit': 'Undersuit',
        'hat': 'Hat',
        'eyes': 'Eyes',
        'hands': 'Hands',
        'jacket': 'Jacket',
        'shirt': 'Shirt',
        'jumpsuit': 'Jumpsuit',
        'pants': 'Pants',
        'shoes': 'Shoes',
    }

    # Suche nach Keywords im Klassennamen
    for keyword, item_type in type_mapping.items():
        if keyword in classname_lower:
            return item_type

    return None


def scrape_wiki_item(url):
    """
    Scraped Daten von einer Star Citizen Wiki Seite.

    Returns:
        dict mit 'name', 'item_type', 'image_url', 'classname'
        oder None bei Fehler
    """
    try:
        print(f"\n🌐 Lade Seite: {url}")

        # Lade HTML
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. ITEM NAME - aus class="mw-page-title-main"
        name_elem = soup.find(class_='mw-page-title-main')
        if not name_elem:
            print("❌ Item-Name nicht gefunden (class='mw-page-title-main')")
            return None

        item_name = name_elem.get_text(strip=True)
        print(f"📝 Name: {item_name}")

        # 2. KLASSENNAME - suche in der Seite nach "Klassenname"
        classname = None
        classname_row = soup.find('th', string=re.compile(r'Klassenname', re.IGNORECASE))
        if classname_row:
            classname_cell = classname_row.find_next_sibling('td')
            if classname_cell:
                classname = classname_cell.get_text(strip=True)
                print(f"🏷️  Klassenname: {classname}")

        if not classname:
            print("⚠️  Klassenname nicht gefunden - versuche weiter...")

        # 3. ITEM TYPE - aus Klassenname ableiten
        item_type = extract_item_type_from_classname(classname)

        if item_type:
            print(f"📦 Item Type erkannt: {item_type}")
        else:
            print(f"⚠️  Item Type konnte nicht automatisch erkannt werden!")
            print("Verfügbare Typen:")
            print("  Helmet, Torso, Arms, Legs, Backpack, Undersuit,")
            print("  Hat, Eyes, Hands, Jacket, Shirt, Jumpsuit, Pants, Shoes")
            item_type = input("Bitte Item Type manuell eingeben: ").strip()

            if not item_type:
                print("❌ Kein Item Type angegeben - Abbruch")
                return None

        # 4. BILD - suche nach Bild-URL
        image_url = None

        # Methode 1: Suche nach <source srcset="...">
        source_elem = soup.find('source', attrs={'srcset': True})
        if source_elem:
            srcset = source_elem.get('srcset', '')
            # Extrahiere erste URL aus srcset (vor dem Komma)
            urls = srcset.split(',')
            if urls:
                image_url = urls[0].strip().split(' ')[0]  # Erste URL ohne Größenangabe

        # Methode 2: Suche nach <a class="image" href="/Datei:...">
        if not image_url:
            image_link = soup.find('a', class_='image', href=re.compile(r'/Datei:'))
            if image_link:
                # Folge dem Link zur Dateiseite
                file_path = image_link.get('href')
                file_url = f"https://star-citizen.wiki{file_path}"

                try:
                    file_response = requests.get(file_url, timeout=10)
                    file_soup = BeautifulSoup(file_response.content, 'html.parser')

                    # Suche nach der Original-Datei
                    original_link = file_soup.find('div', class_='fullImageLink')
                    if original_link:
                        img_tag = original_link.find('a')
                        if img_tag:
                            image_url = img_tag.get('href')
                            if image_url and not image_url.startswith('http'):
                                image_url = f"https://star-citizen.wiki{image_url}"
                except Exception as e:
                    print(f"⚠️  Fehler beim Laden der Dateiseite: {e}")

        # Methode 3: Direkte Suche nach <img> in der Infobox
        if not image_url:
            infobox_img = soup.find('table', class_='infobox').find('img') if soup.find('table', class_='infobox') else None
            if infobox_img:
                image_url = infobox_img.get('src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"https://star-citizen.wiki{image_url}"

        if image_url:
            print(f"🖼️  Bild URL: {image_url}")
        else:
            print("⚠️  Kein Bild gefunden - Item wird ohne Bild importiert")

        return {
            'name': item_name,
            'item_type': item_type,
            'image_url': image_url,
            'classname': classname
        }

    except requests.RequestException as e:
        print(f"❌ Fehler beim Laden der Seite: {e}")
        return None
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return None


def download_and_convert_image(image_url):
    """
    Lädt Bild herunter, konvertiert zu PNG und speichert temporär.

    Returns:
        Pfad zur temporären PNG-Datei oder None
    """
    try:
        print(f"⬇️  Lade Bild herunter...")

        response = requests.get(image_url, timeout=15)
        response.raise_for_status()

        # Speichere temporär
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        # Öffne mit PIL und konvertiere zu PNG
        img = Image.open(tmp_path)

        # Konvertiere zu RGB falls nötig (für CMYK, etc.)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        # Speichere als PNG
        png_path = tmp_path + '.png'
        img.save(png_path, 'PNG')

        # Lösche temporäre Originaldatei
        try:
            os.remove(tmp_path)
        except:
            pass

        print(f"✅ Bild heruntergeladen und zu PNG konvertiert")
        return png_path

    except Exception as e:
        print(f"❌ Fehler beim Bilddownload: {e}")
        return None


def import_item_to_database(api, item_data, image_temp_path):
    """
    Importiert Item in die Datenbank mit Bild.

    Args:
        api: API Instanz
        item_data: Dict mit 'name', 'item_type', 'image_url'
        image_temp_path: Pfad zur temporären PNG-Datei oder None

    Returns:
        bool: True bei Erfolg
    """
    try:
        # Prüfe ob Item bereits existiert
        existing = api.get_item(item_data['name'])

        if existing:
            print(f"\n⚠️  Item '{item_data['name']}' existiert bereits in der Datenbank!")
            overwrite = input("Möchtest du es überschreiben? (ja/nein): ").strip().lower()

            if overwrite not in ['ja', 'j', 'yes', 'y']:
                print("❌ Import abgebrochen")
                return False

            # Lösche alte Bilder
            if existing.get('image_path') and os.path.exists(existing['image_path']):
                try:
                    base_path = os.path.splitext(existing['image_path'])[0]
                    for suffix in ['', '_thumb.png', '_medium.png']:
                        old_file = existing['image_path'] if suffix == '' else base_path + suffix
                        if os.path.exists(old_file):
                            os.remove(old_file)
                            print(f"🗑️  Alte Datei gelöscht: {old_file}")
                except Exception as e:
                    print(f"⚠️  Warnung: Alte Dateien konnten nicht gelöscht werden: {e}")

        # Speichere Bild im Cache (generiert automatisch _thumb.png und _medium.png)
        image_path = None
        if image_temp_path and item_data['image_url']:
            print(f"\n💾 Speichere Bild im Cache...")
            image_path = api.cache.save_image(
                item_data['image_url'],
                image_temp_path,
                item_data['item_type']
            )

            if image_path:
                print(f"✅ Bild gespeichert: {image_path}")

                # Prüfe ob Thumbnails erstellt wurden
                base_path = os.path.splitext(image_path)[0]
                thumb_path = f"{base_path}_thumb.png"
                medium_path = f"{base_path}_medium.png"

                if os.path.exists(thumb_path):
                    print(f"✅ Thumbnail erstellt: {thumb_path}")
                if os.path.exists(medium_path):
                    print(f"✅ Medium erstellt: {medium_path}")
            else:
                print(f"⚠️  Bild konnte nicht gespeichert werden")

        # Füge Item zur Datenbank hinzu oder aktualisiere es
        if existing:
            # Update existierendes Item
            api.db.conn.execute(
                """UPDATE items
                   SET item_type = ?, image_url = ?, image_path = ?
                   WHERE name = ?""",
                (item_data['item_type'], item_data['image_url'], image_path, item_data['name'])
            )
            api.db.conn.commit()
            print(f"\n✅ Item '{item_data['name']}' wurde aktualisiert!")
        else:
            # Neues Item hinzufügen
            result = api.add_item(
                name=item_data['name'],
                item_type=item_data['item_type'],
                image_url=item_data['image_url'],
                notes=None,
                initial_count=0  # Count = 0, nur zur Datenbank hinzufügen
            )

            if result.get('success'):
                print(f"\n✅ Item '{item_data['name']}' wurde zur Datenbank hinzugefügt!")
            else:
                print(f"\n❌ Fehler beim Hinzufügen: {result.get('error')}")
                return False

        return True

    except Exception as e:
        print(f"\n❌ Fehler beim Import: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 80)
    print("SINGLE IMPORT - Star Citizen Wiki Item Importer")
    print("=" * 80)
    print()
    print("Importiere einzelne Items von Star Citizen Wiki URLs")
    print("Beispiel: https://star-citizen.wiki/ADP_Core")
    print()
    print("Drücke Ctrl+C zum Beenden")
    print("=" * 80)
    print()

    # Initialize API
    api = API()

    while True:
        try:
            # Warte auf URL-Eingabe
            url = input("\n🔗 Bitte Wiki-URL eingeben (oder 'exit' zum Beenden): ").strip()

            if url.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Auf Wiedersehen!")
                break

            if not url:
                print("⚠️  Keine URL eingegeben")
                continue

            if not url.startswith('http'):
                print("⚠️  Ungültige URL - muss mit http:// oder https:// beginnen")
                continue

            print("\n" + "=" * 80)

            # 1. Scrape Item-Daten von der Wiki-Seite
            item_data = scrape_wiki_item(url)

            if not item_data:
                print("\n❌ Konnte Item-Daten nicht extrahieren - überspringe")
                continue

            # 2. Lade Bild herunter (falls vorhanden)
            image_temp_path = None
            if item_data['image_url']:
                image_temp_path = download_and_convert_image(item_data['image_url'])

            # 3. Importiere in Datenbank
            success = import_item_to_database(api, item_data, image_temp_path)

            # 4. Cleanup temporäre Datei
            if image_temp_path and os.path.exists(image_temp_path):
                try:
                    os.remove(image_temp_path)
                except:
                    pass

            if success:
                print("\n" + "=" * 80)
                print("✅ IMPORT ERFOLGREICH")
                print("=" * 80)
            else:
                print("\n" + "=" * 80)
                print("❌ IMPORT FEHLGESCHLAGEN")
                print("=" * 80)

        except KeyboardInterrupt:
            print("\n\n⚠️ Import abgebrochen!")
            break
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()

    input("\nDrücke Enter zum Beenden...")
