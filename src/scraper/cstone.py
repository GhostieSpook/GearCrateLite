"""
CStone.space scraper to fetch item images and data
"""
import os
import requests
from bs4 import BeautifulSoup
import re
import time


class CStoneScraper:
    BASE_URL = "https://finder.cstone.space"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_item(self, item_name):
        """Search for an item on CStone"""
        try:
            # Search URL
            search_url = f"{self.BASE_URL}/Search"
            params = {'search': item_name}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find item links (this is a simplified example, may need adjustment)
            # CStone structure might vary, this is a starting point
            results = []
            
            # Look for item cards or links
            item_elements = soup.find_all('a', href=re.compile(r'/FPSArmors1/|/Search/'))
            
            for element in item_elements[:10]:  # Limit to first 10 results
                item_href = element.get('href')
                item_text = element.get_text(strip=True)
                
                if item_text and item_href:
                    results.append({
                        'name': item_text,
                        'url': f"{self.BASE_URL}{item_href}" if not item_href.startswith('http') else item_href
                    })
            
            return results
        
        except Exception as e:
            print(f"Error searching item: {e}")
            return []
    
    def get_item_image(self, item_url):
        """Get image URL from item page"""
        try:
            response = self.session.get(item_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image - CStone usually has images in specific tags
            # This might need adjustment based on actual page structure
            img_tag = soup.find('img', src=re.compile(r'\.(jpg|jpeg|png|webp)'))
            
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                if not img_url.startswith('http'):
                    img_url = f"{self.BASE_URL}{img_url}"
                return img_url
            
            return None
        
        except Exception as e:
            print(f"Error fetching image: {e}")
            return None
    
    def download_image(self, image_url, save_path):
        """Download image from URL to local path"""
        try:
            print(f"    Downloading: {image_url}")
            response = self.session.get(image_url, timeout=15, stream=True)
            
            # Check if successful
            if response.status_code == 404:
                print(f"    ✗ Image not found (404): {image_url}")
                return False
            
            response.raise_for_status()
            
            # Save image
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file was created and has content
            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                print(f"    ✓ Image downloaded: {os.path.getsize(save_path)} bytes")
                return True
            else:
                print(f"    ✗ Downloaded file is empty or doesn't exist")
                return False
        
        except Exception as e:
            print(f"    ✗ Error downloading image: {e}")
            return False
