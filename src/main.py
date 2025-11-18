"""
Star Citizen Inventory Manager
Main entry point
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gui.window import Window


def main():
    """Main application entry point"""
    print("Starting SC Inventory Manager...")
    
    app = Window()
    app.start()


if __name__ == '__main__':
    main()
