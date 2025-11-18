"""
Test Scraper - Analysiert die HTML-Struktur von CStone.space
"""
import requests
from bs4 import BeautifulSoup

url = "https://finder.cstone.space/FPSArmors?type=Torsos"

print("Lade:", url)
print()

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

response = session.get(url, timeout=10)
print(f"Status Code: {response.status_code}")
print()

soup = BeautifulSoup(response.content, 'html.parser')

# Speichere HTML zur Analyse
with open('cstone_debug.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("HTML gespeichert in: cstone_debug.html")
print()

# Zeige erste 2000 Zeichen
print("=" * 60)
print("HTML Preview (erste 2000 Zeichen):")
print("=" * 60)
print(soup.prettify()[:2000])
print()
print("...")
print()

# Suche nach verschiedenen Elementen
print("=" * 60)
print("Element-Analyse:")
print("=" * 60)

print(f"Alle <a> Tags: {len(soup.find_all('a'))}")
print(f"Alle <table> Tags: {len(soup.find_all('table'))}")
print(f"Alle <div> Tags: {len(soup.find_all('div'))}")
print(f"Alle <tr> Tags: {len(soup.find_all('tr'))}")
print()

# Zeige erste 10 Links
links = soup.find_all('a', limit=10)
if links:
    print("Erste 10 Links:")
    for i, link in enumerate(links, 1):
        href = link.get('href', 'N/A')
        text = link.get_text(strip=True)
        print(f"  {i}. Text: '{text[:50]}' | Href: '{href[:60]}'")
else:
    print("Keine Links gefunden!")

print()
print("Fertig! Schau dir cstone_debug.html an.")
