"""
CStone API Analyzer - Findet heraus wie CStone Daten lädt
"""
import requests
import json

base_url = "https://finder.cstone.space"

print("=" * 60)
print("CStone API Analyzer")
print("=" * 60)
print()

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Teste verschiedene mögliche API Endpoints
endpoints = [
    "/api/items",
    "/api/armor",
    "/api/FPSArmors",
    "/FPSArmors/list",
    "/Search",
    "/api/search",
]

print("Teste API Endpoints...")
print("-" * 60)

for endpoint in endpoints:
    url = base_url + endpoint
    try:
        response = session.get(url, timeout=10)
        print(f"\n{endpoint}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"  Content-Type: {content_type}")
            
            if 'json' in content_type:
                try:
                    data = response.json()
                    print(f"  JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                    print(f"  Preview: {str(data)[:200]}...")
                except:
                    print(f"  JSON Parse Error")
            else:
                print(f"  Size: {len(response.content)} bytes")
                print(f"  Preview: {response.text[:200]}...")
    
    except Exception as e:
        print(f"\n{endpoint}")
        print(f"  Error: {e}")

print()
print("=" * 60)
print("Versuche direkten Zugriff auf Item-Seite...")
print("=" * 60)

# Versuche eine spezifische Item-Seite
item_url = base_url + "/FPSArmors1/"
try:
    response = session.get(item_url, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Size: {len(response.content)} bytes")
    
    # Speichere für Analyse
    with open('cstone_item_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Gespeichert in: cstone_item_page.html")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("Fertig! Schau dir die Dateien an.")
print("=" * 60)
