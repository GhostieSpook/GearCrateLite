"""
CSV Importer - Importiert Items aus einer CSV-Datei
Format: Name,Type,Notes
"""
import sys
import os
import csv

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import Database
from database.operations import ItemOperations


def import_from_csv(filename='items.csv'):
    """Importiert Items aus CSV"""
    
    if not os.path.exists(filename):
        print(f"Fehler: Datei '{filename}' nicht gefunden!")
        print()
        print("Erstelle Beispiel-Datei...")
        
        # Create example CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Type', 'Notes'])
            writer.writerow(['Morozov-SH Core', 'Torso', 'Heavy armor'])
            writer.writerow(['Pembroke Backpack', 'Backpack', ''])
            writer.writerow(['Novikov Helmet', 'Helmet', 'Cold weather'])
        
        print(f"Beispiel-Datei '{filename}' erstellt!")
        print("Bearbeite die Datei und füge deine Items hinzu.")
        return
    
    db = Database()
    operations = ItemOperations(db)
    
    print("=" * 60)
    print("CSV Import")
    print("=" * 60)
    print()
    
    imported = 0
    skipped = 0
    errors = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, 2):  # Start at 2 (header is row 1)
            try:
                name = row.get('Name', '').strip()
                item_type = row.get('Type', '').strip() or None
                notes = row.get('Notes', '').strip() or None
                
                if not name:
                    continue
                
                # Check if exists
                existing = operations.get_item_by_name(name)
                if existing:
                    print(f"⏭️  [Zeile {row_num}] '{name}' bereits vorhanden")
                    skipped += 1
                    continue
                
                # Import
                result = operations.add_item(
                    name=name,
                    item_type=item_type,
                    image_url=None,
                    image_path=None,
                    notes=notes
                )
                
                if result['success']:
                    print(f"✅ [Zeile {row_num}] '{name}' importiert")
                    imported += 1
                else:
                    print(f"❌ [Zeile {row_num}] Fehler bei '{name}'")
                    errors += 1
            
            except Exception as e:
                print(f"❌ [Zeile {row_num}] Fehler: {e}")
                errors += 1
    
    print()
    print("=" * 60)
    print(f"Import abgeschlossen!")
    print(f"Importiert: {imported}")
    print(f"Übersprungen: {skipped}")
    print(f"Fehler: {errors}")
    print("=" * 60)
    
    db.close()


if __name__ == '__main__':
    import_from_csv('items.csv')
    print()
    input("Enter drücken zum Beenden...")
