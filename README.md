## GearCrate Star Citizen Inventory Manager

A desktop tool designed for managing and tracking your collected armor, clothing, and items within your Star Citizen inventory.

### Key Features

* Inventory Management: Track your collection with item images and personal notes.
* Live Search: Search and import item details directly from CStone.space.
* Local Storage: All inventory data and cached images are stored locally on your PC using an SQLite database.
* Gear-Sets: Keep up to date which armor set you completed or which part is missing.
* Import from SC: Scan your Star Citizen inventory and import it into the GearCrate inventory.

---

## Download

Download the latest test version here: https://github.com/KruemelGames/GearCrate/releases/tag/Test

## Installation & Launch (Optimized Workflow)

This project requires **Python 3.8 or higher** to run.

### 1. One-Time Setup (First Use)

For a complete installation of all dependencies and an automatic initial launch, use the consolidated setup script:

1.  Ensure **Python** is already installed and accessible on your system.
2.  Double-click to run **`setup.bat`**.

> **Note:** The **`setup.bat`** script automatically installs all required Python libraries from the `requirements.txt` file, verifies the Python version, and launches the application upon successful completion.

### 2. Daily Application Launch

To start the program for routine use after the initial setup:

1.  Double-click to run **`start-browser.bat`**.

> **Note:** This script initiates the local Python backend server and automatically opens the application window (GUI) once the server is ready.

---


## Usage

1.  **Add an Item:** Enter the item name into the search bar and select the item from the CStone search results to add it to your collection.
2.  **Manage Inventory:** Use the filter bar to search your items and edit quantities or notes for individual entries.
