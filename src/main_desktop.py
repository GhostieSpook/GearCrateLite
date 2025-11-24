"""
GearCrate - Desktop Mode (pywebview + HTTP Server)
- HTTP server running in background thread
- pywebview window for desktop experience
- Ready for hotkey integration
"""
import os
import sys
import threading
import time
from http.server import HTTPServer

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from main_browser import GearCrateAPIHandler
from api.backend import API
import webview


class DesktopServer:
    """Desktop server with pywebview"""
    
    def __init__(self, port=8080):
        self.port = port
        self.httpd = None
        self.server_thread = None
        self.api = None
        
    def start_http_server(self):
        """Start HTTP server in background thread"""
        print("🔧 Starting HTTP server...")
        
        # Initialize API
        self.api = API()
        GearCrateAPIHandler.api = self.api
        
        # Set cache directory
        GearCrateAPIHandler.cache_dir = os.path.join(project_root, 'data', 'cache', 'images')
        
        # Change to web directory
        web_dir = os.path.join(project_root, 'web')
        os.chdir(web_dir)
        
        # Create server
        server_address = ('', self.port)
        self.httpd = HTTPServer(server_address, GearCrateAPIHandler)
        
        # Start in background thread
        self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.server_thread.start()
        
        print(f"✅ HTTP Server running on http://localhost:{self.port}")
        
        # Wait a bit to ensure server is ready
        time.sleep(0.5)
    
    def start_desktop_window(self):
        """Start pywebview window"""
        print("🖥️  Opening desktop window...")
        
        # Create window pointing to localhost
        window = webview.create_window(
            'GearCrate - Star Citizen Inventory Manager',
            f'http://localhost:{self.port}/index.html',
            width=1400,
            height=900,
            resizable=True,
            background_color='#1a1a1a',
            confirm_close=False
        )
        
        print("✅ Desktop window ready!")
        print("=" * 60)
        print("📦 GearCrate is running!")
        print("=" * 60)
        
        # Start webview (blocking)
        webview.start(debug=True)
        
    def start(self):
        """Start the complete desktop application"""
        try:
            # 1. Start HTTP server in background
            self.start_http_server()
            
            # 2. Start desktop window (blocking)
            self.start_desktop_window()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup on exit"""
        print("🧹 Cleaning up...")
        
        if self.httpd:
            self.httpd.shutdown()
        
        if self.api and hasattr(self.api, 'close'):
            self.api.close()
        
        print("✅ GearCrate stopped!")


def main():
    """Main entry point"""
    print("=" * 60)
    print("📦 GearCrate - Desktop Mode")
    print("=" * 60)
    print()
    
    server = DesktopServer(port=8080)
    server.start()


if __name__ == '__main__':
    main()
