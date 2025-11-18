"""
API Backend for frontend communication
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
        """Search items in local database with THUMBNAILS"""
        if not query:
            items = self.operations.get_all_items()
        else:
            items = self.operations.search_items(query)
        
        # Add image URLs for frontend (icon for search, thumb for inventory, full for modal)
        for item in items:
            if item.get('image_path'):
                item['icon_url'] = self._get_icon_url(item['image_path'])
                item['thumb_url'] = self._get_thumb_url(item['image_path'])
                item['full_url'] = self._get_full_url(item['image_path'])
        
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
            cached_path = self.cache.get_cached_path(image_url, item_type)
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
                        image_path = self.cache.save_image(image_url, temp_path, item_type)
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
                # Add image URLs
                item_data['icon_url'] = self._get_icon_url(item_data['image_path'])
                item_data['thumb_url'] = self._get_thumb_url(item_data['image_path'])
                item_data['full_url'] = self._get_full_url(item_data['image_path'])
            return {'success': True, 'item': item_data}
        
        return result
    
    def get_item(self, name):
        """Get item by name with image URLs"""
        item = self.operations.get_item_by_name(name)
        if item and item.get('image_path'):
            # Add all image URLs
            item['icon_url'] = self._get_icon_url(item['image_path'])
            item['thumb_url'] = self._get_thumb_url(item['image_path'])
            item['full_url'] = self._get_full_url(item['image_path'])
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
        
        # Items in Datenbank (alle)
        total_items = len(all_items)
        
        # Items im Inventar (count > 0)
        inventory_items = [item for item in all_items if item.get('count', 0) > 0]
        inventory_unique_items = len(inventory_items)
        
        # Gesamtzahl (Summe aller Counts)
        total_count = sum(item['count'] for item in all_items)
        
        # Kategorie-Statistiken (nur Kategorien mit count > 0)
        category_counts = {}
        for item in inventory_items:
            item_type = item.get('item_type', 'Unbekannt')
            if item_type:
                category_counts[item_type] = category_counts.get(item_type, 0) + item.get('count', 0)
        
        # Cache-Größe
        cache_size = self.cache.get_cache_size()
        
        return {
            'total_items_in_db': total_items,
            'inventory_unique_items': inventory_unique_items,
            'total_item_count': total_count,
            'category_counts': category_counts,
            'cache_size_mb': round(cache_size / (1024 * 1024), 2)
        }
    
    def get_categories(self):
        """Get all unique item categories/types"""
        all_items = self.operations.get_all_items()
        categories = set()
        
        for item in all_items:
            if item.get('item_type'):
                categories.add(item['item_type'])
        
        return sorted(list(categories))
    
    def get_inventory_items(self, sort_by='name', sort_order='asc', category_filter=None):
        """Get only items with count > 0, with THUMBNAIL URLs for performance
        
        Args:
            sort_by: Sort field ('name', 'count', 'date')
            sort_order: Sort order ('asc' or 'desc')
            category_filter: Optional category to filter by
        """
        all_items = self.operations.get_all_items()
        
        # Filter: only items with count > 0
        inventory_items = [item for item in all_items if item.get('count', 0) > 0]
        
        # Category filter
        if category_filter:
            inventory_items = [item for item in inventory_items 
                             if item.get('item_type') == category_filter]
        
        # Sorting
        reverse = (sort_order == 'desc')
        if sort_by == 'name':
            inventory_items.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse)
        elif sort_by == 'count':
            inventory_items.sort(key=lambda x: x.get('count', 0), reverse=reverse)
        elif sort_by == 'date':
            # Sortiere nach added_to_inventory_at (wann Item ins Inventar kam)
            # Items ohne Datum kommen ans Ende
            inventory_items.sort(
                key=lambda x: x.get('added_to_inventory_at') or '1900-01-01', 
                reverse=reverse
            )
        
        # Add image URLs (icon, thumb, full) instead of base64
        for item in inventory_items:
            if item.get('image_path'):
                item['icon_url'] = self._get_icon_url(item['image_path'])
                item['thumb_url'] = self._get_thumb_url(item['image_path'])
                item['full_url'] = self._get_full_url(item['image_path'])
        
        return inventory_items
    
    def _get_icon_url(self, image_path):
        """Get icon URL for search results - uses THUMB (256x256)"""
        if not image_path or not os.path.exists(image_path):
            return None
        
        # Try to find thumbnail version
        base_path = os.path.splitext(image_path)[0]
        thumb_path = f"{base_path}_thumb.png"
        
        # If thumbnail doesn't exist, use original
        if not os.path.exists(thumb_path):
            thumb_path = image_path
        
        return self._path_to_url(thumb_path)
    
    def _get_thumb_url(self, image_path):
        """Get thumbnail URL for inventory grid - uses MEDIUM (512x512)"""
        if not image_path or not os.path.exists(image_path):
            return None
        
        # Try to find medium version
        base_path = os.path.splitext(image_path)[0]
        medium_path = f"{base_path}_medium.png"
        
        # If medium doesn't exist, use original
        if not os.path.exists(medium_path):
            medium_path = image_path
        
        return self._path_to_url(medium_path)
    
    def _get_full_url(self, image_path):
        """Get full image URL (original resolution) for modal"""
        if not image_path or not os.path.exists(image_path):
            return None
        
        return self._path_to_url(image_path)
    
    def _path_to_url(self, file_path):
        """Convert file path to URL for frontend
        
        Converts paths like:
        C:\\Users\\kruem\\...\\data\\cache\\images\\Eyes\\abc123_thumb.png
        to:
        /cache/Eyes/abc123_thumb.png
        """
        if not file_path or not os.path.exists(file_path):
            return None
        
        try:
            # Normalize path separators to forward slashes
            normalized_path = file_path.replace('\\', '/')
            
            # Look for 'data/cache/images/' in the path
            marker = 'data/cache/images/'
            idx = normalized_path.find(marker)
            
            if idx == -1:
                # Try with leading slash
                marker = '/data/cache/images/'
                idx = normalized_path.find(marker)
            
            if idx != -1:
                # Extract everything after 'data/cache/images/'
                # e.g., 'Eyes/abc123.png' or 'Eyes/abc123_thumb.png'
                relative_path = normalized_path[idx + len(marker):]
                return f'/cache/{relative_path}'
            
            print(f"  Warning: Could not convert path to URL: {file_path}")
            return None
        except Exception as e:
            print(f"  Error converting path to URL ({file_path}): {e}")
            import traceback
            traceback.print_exc()
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
