"""
Generate thumbnails for existing images
Run this once to create thumbnails for all images that don't have them yet
"""
import os
import sys
from PIL import Image

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from cache.image_cache import ImageCache


def generate_thumbnails_for_existing():
    """Generate thumbnails for all existing images"""
    cache = ImageCache()
    cache_dir = cache.cache_dir
    
    print("Scanning for images without thumbnails...")
    print(f"Cache directory: {cache_dir}")
    
    count = 0
    total = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(cache_dir):
        for filename in files:
            # Skip if it's already a thumbnail or medium
            if '_thumb' in filename or '_medium' in filename:
                continue
            
            # Skip .gitkeep
            if filename == '.gitkeep':
                continue
            
            # Check if it's an image
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                continue
            
            filepath = os.path.join(root, filename)
            base_path = os.path.splitext(filepath)[0]
            thumb_path = f"{base_path}_thumb.png"
            medium_path = f"{base_path}_medium.png"
            
            # Check if thumbnails already exist
            if os.path.exists(thumb_path) and os.path.exists(medium_path):
                continue
            
            total += 1
            
            try:
                print(f"Generating thumbnails for: {filename}")
                img = Image.open(filepath)
                
                # Generate thumbnail (64x64)
                if not os.path.exists(thumb_path):
                    thumb_img = img.copy()
                    thumb_img.thumbnail((64, 64), Image.Resampling.LANCZOS)
                    thumb_img.save(thumb_path, 'PNG', optimize=True)
                    print(f"  ✓ Created thumbnail: {thumb_path}")
                
                # Generate medium (256x256)
                if not os.path.exists(medium_path):
                    medium_img = img.copy()
                    medium_img.thumbnail((256, 256), Image.Resampling.LANCZOS)
                    medium_img.save(medium_path, 'PNG', optimize=True)
                    print(f"  ✓ Created medium: {medium_path}")
                
                count += 1
                
            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Finished!")
    print(f"Processed: {count}/{total} images")
    print(f"{'='*50}")


if __name__ == '__main__':
    print("="*50)
    print("Thumbnail Generator")
    print("="*50)
    print()
    
    generate_thumbnails_for_existing()
    
    print()
    input("Press Enter to exit...")
