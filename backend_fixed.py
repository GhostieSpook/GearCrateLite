"""
API Backend for frontend communication - FIXED VERSION for FPSClothes support
"""
import os
import base64
import sys

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
        """Search items in local database"""
        if not query:
            items = self.operations.get_all_items()
        else:
            items = self.operations.search_items(query)
        
        # Add image_base64 to each item
        for item in items:
            if item.get('image_path'):
                item['image_base64'] = self._get_image_base64(item['image_path'])
        
        return items
    
    def search_items_cstone(self, query):
        """Search items on CStone.space"""
        if not query or len(query) < 2:
            return []
        
        results = self.scraper.search_item(query)
        return results
    
    def add_item(self, name, item_type=None, image_url=None, notes=None, initial_count=1):
        """Add item to inventory
        
        Args:
            initial_count: Starting count for new items (default 1, use 0 for imports)
        """
        # Download and cache image regardless of initial_count
        image_path = None
        if image_url:
            print(f"  Processing image for '{name}': {image_url}")
            cached_path = self.cache.get_cached_path(image_url)
            if cached_path:
                print(f"  ✓ Using cached image: {cached_path}")
                image_path = cached_path
            else:
                # Download and cache image
                print(f"  Downloading new image...")
                
                # Ensure cache directory exists
                os.makedirs(self.cache.cache_dir, exist_ok=True)
                
                # Use absolute path for temp file
                import tempfile
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png', dir=self.cache.cache_dir)
                os.close(temp_fd)  # Close file descriptor, we'll write with requests
                
                try:
                    if self.scraper.download_image(image_url, temp_path):
                        image_path = self.cache.save_image(image_url, temp_path)
                        print(f"  ✓ Image saved to: {image_path}")
                    else:
                        print(f"  ✗ Image download failed")
                    
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as e:
                    print(f"  ✗ Exception during image download: {e}")
                    import traceback
                    traceback.print_exc()
                    # Clean up temp file on error
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            print(f"  No image URL provided for '{name}'")
        
        result = self.operations.add_item(name, item_type, image_url, image_path, notes, initial_count)
        
        # Get updated item data
        if result['success']:
            item_data = self.operations.get_item_by_name(name)
            if item_data and item_data.get('image_path'):
                # Convert image to base64 for frontend
                item_data['image_base64'] = self._get_image_base64(item_data['image_path'])
            return {'success': True, 'item': item_data}
        
        return result
    
    def get_item(self, name):
        """Get item by name"""
        item = self.operations.get_item_by_name(name)
        if item and item.get('image_path'):
            item['image_base64'] = self._get_image_base64(item['image_path'])
        return item
    
    def update_count(self, name, count):
        """Update item count"""
        return self.operations.update_count(name, max(0, count))
    
    def update_notes(self, name, notes):
        """Update item notes"""
        return self.operations.update_notes(name, notes)
    
    def delete_item(self, name):
        """Delete item from inventory"""
        return self.operations.delete_item(name)
    
    def clear_inventory(self):
        """Set all item counts to 0 (empty inventory but keep items)"""
        return self.operations.clear_inventory()
    
    def delete_all_items(self):
        """Delete ALL items from database"""
        return self.operations.delete_all_items()
    
    def clear_cache(self):
        """Clear image cache"""
        try:
            import shutil
            cache_dir = self.cache.cache_dir
            if os.path.exists(cache_dir):
                # Delete all files in cache
                for filename in os.listdir(cache_dir):
                    if filename != '.gitkeep':
                        filepath = os.path.join(cache_dir, filename)
                        try:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                        except Exception as e:
                            print(f"Error deleting {filepath}: {e}")
                return {'success': True, 'message': 'Cache cleared'}
            return {'success': False, 'error': 'Cache directory not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_stats(self):
        """Get inventory statistics"""
        all_items = self.operations.get_all_items()
        total_items = len(all_items)
        total_count = sum(item['count'] for item in all_items)
        cache_size = self.cache.get_cache_size()
        
        return {
            'total_unique_items': total_items,
            'total_item_count': total_count,
            'cache_size_mb': round(cache_size / (1024 * 1024), 2)
        }
    
    def _get_image_base64(self, image_path):
        """Convert image to base64 string for frontend display"""
        try:
            if not image_path:
                return None
                
            if not os.path.exists(image_path):
                print(f"  Warning: Image file not found: {image_path}")
                return None
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            if len(image_data) == 0:
                print(f"  Warning: Image file is empty: {image_path}")
                return None
            
            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/png')
            
            base64_str = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_str}"
        
        except Exception as e:
            print(f"  Error converting image to base64 ({image_path}): {e}")
            return None
    
    def get_category_items(self, category_url):
        """Get all items from a CStone category (supports both FPSArmors and FPSClothes)"""
        try:
            import urllib.parse
            from bs4 import BeautifulSoup
            import re
            
            # Decode URL-encoded path
            category_url = urllib.parse.unquote(category_url)
            
            # Determine if this is FPSArmors or FPSClothes
            is_clothes = 'FPSClothes' in category_url
            
            # Full URL to CStone
            full_url = f"https://finder.cstone.space/{category_url}"
            
            print(f"Fetching items from: {full_url}")
            print(f"Category type: {'FPSClothes' if is_clothes else 'FPSArmors'}")
            
            response = self.scraper.session.get(full_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = []
            
            # Find all table rows (CStone uses DataTables)
            # The actual data is often loaded via AJAX, but we can try to parse the HTML
            rows = soup.find_all('tr')
            
            for row in rows:
                # Skip header rows
                cells = row.find_all('td')
                if len(cells) < 3:  # Need at least name and type
                    continue
                
                # Extract item name (usually first visible column)
                name_cell = cells[0]
                item_name = name_cell.get_text(strip=True)
                
                if not item_name or item_name == '❐':
                    continue
                
                # Try to find link to item detail page (different patterns for armor vs clothes)
                if is_clothes:
                    link = row.find('a', href=re.compile(r'/FPSClothes1/'))
                else:
                    link = row.find('a', href=re.compile(r'/FPSArmors1/'))
                
                item_url = None
                image_url = None
                
                if link:
                    item_url = link.get('href')
                    if item_url and not item_url.startswith('http'):
                        item_url = f"https://finder.cstone.space{item_url}"
                    
                    # Extract item ID from URL for image
                    if item_url:
                        if is_clothes:
                            match = re.search(r'/FPSClothes1/(\d+)', item_url)
                        else:
                            match = re.search(r'/FPSArmors1/(\d+)', item_url)
                        
                        if match:
                            item_id = match.group(1)
                            image_url = f"https://cstone.space/uifimages/{item_id}.png"
                
                items.append({
                    'name': item_name,
                    'url': item_url,
                    'image_url': image_url
                })
            
            # Alternative: Try to find items via JavaScript data
            # Some pages load data via AJAX from /GetArmors/ or /GetClothes/ endpoint
            if len(items) == 0:
                # Try to extract category type from URL
                type_match = re.search(r'type=([^&]+)', category_url)
                if type_match:
                    item_type = type_match.group(1)
                    
                    # Choose correct AJAX endpoint based on category
                    if is_clothes:
                        ajax_url = f"https://finder.cstone.space/GetClothes/{item_type}"
                    else:
                        ajax_url = f"https://finder.cstone.space/GetArmors/{item_type}"
                    
                    print(f"Trying AJAX endpoint: {ajax_url}")
                    
                    ajax_response = self.scraper.session.get(ajax_url, timeout=15)
                    ajax_response.raise_for_status()
                    
                    ajax_data = ajax_response.json()
                    
                    for item_data in ajax_data:
                        item_id = item_data.get('ItemId')
                        item_name = item_data.get('Name')
                        
                        if item_name and item_id:
                            if is_clothes:
                                detail_url = f"https://finder.cstone.space/FPSClothes1/{item_id}"
                            else:
                                detail_url = f"https://finder.cstone.space/FPSArmors1/{item_id}"
                            
                            items.append({
                                'name': item_name,
                                'url': detail_url,
                                'image_url': f"https://cstone.space/uifimages/{item_id}.png"
                            })
            
            print(f"Found {len(items)} items in category")
            return items
        
        except Exception as e:
            print(f"Error fetching category items: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def close(self):
        """Close database connection"""
        self.db.close()
