"""
Manueller Import aus Textdatei
"""
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import Database
from database.operations import ItemOperations


def import_from_file(filename='items_to_import.txt'):
    """Importiert Items aus einer Textdatei"""
    
    if not os.path.exists(filename):
        print(f"Fehler: Datei '{filename}' nicht gefunden!")
        return
    
    db = Database()
    operations = ItemOperations(db)
    
    print("=" * 60)
    print("Manueller Import aus Textdatei")
    print("=" * 60)
    print()
    
    imported = 0
    skipped = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse line
            parts = line.split('|')
            item_name = parts[0].strip()
            item_type = parts[1].strip() if len(parts) > 1 else None
            
            if not item_name:
                continue
            
            # Check if exists
            existing = operations.get_item_by_name(item_name)
            if existing:
                print(f"⏭️  [{line_num}] '{item_name}' bereits vorhanden")
                skipped += 1
                continue
            
            # Import
            result = operations.add_item(
                name=item_name,
                item_type=item_type,
                image_url=None,
                image_path=None,
                notes="Manually imported"
            )
            
            if result['success']:
                print(f"✅ [{line_num}] '{item_name}' importiert")
                imported += 1
            else:
                print(f"❌ [{line_num}] Fehler bei '{item_name}'")
    
    print()
    print("=" * 60)
    print(f"Import abgeschlossen!")
    print(f"Importiert: {imported}")
    print(f"Übersprungen: {skipped}")
    print("=" * 60)
    
    db.close()


if __name__ == '__main__':
    import_from_file('items_to_import.txt')
    print()
    input("Enter drücken zum Beenden...")
