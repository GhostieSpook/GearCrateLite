# 📦 GearCrate Lite (Linux Edition)

GearCrate Lite is a lightweight Flask web application for tracking Star Citizen gear and inventory.  
This project is a **remix and simplified rebuild** of the original GearCrate by KruemelGames:  
👉 https://github.com/KruemelGames/GearCrate

GearCrate Lite focuses on minimal setup, fast performance, and local-only storage.

---

## 🐧 Built for Linux

Designed for:

- Ubuntu / Debian / Linux Mint  
- Arch / Manjaro  
- Fedora / RHEL  
- Raspberry Pi OS (ARM)

---

## 🚀 Features

- Flask-based lightweight web UI  
- SQLite database auto-created on first launch  
- Add, edit, delete, and view items  
- Automatic merging (same name + category + location)  
- Optional image URLs  
- Star Citizen Wiki autocomplete with thumbnails & short descriptions  
- No external database or cloud dependency  
- Fully local, fast, and private  

---

## 📂 Project Structure

```
GearCrateLite/
│
├── app.py
├── inventory.db
├── README.md
├── requirements.txt
│
├── static/
│   ├── css/
│   │   └── styles.css
│   └── img/
│       └── logos/
│           ├── GearCrate_Anim.gif
│           ├── GearCrate_Logo.png
│           ├── GearCrate_title.png
│           └── GearCrate_Title.psd
│
└── templates/
    ├── index.html
    ├── edit_item.html
    └── view_item.html
```

---

## 📚 Requirements

### Install Linux dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip
```

*(Use equivalent packages for Arch/Fedora/etc.)*

### Python dependencies (from requirements.txt)

```
Flask
requests
```

---

## 🔧 Installation

### 1. Extract or Clone the Project

```bash
unzip GearCrateLite.zip
cd GearCrateLite
```

—or—

```bash
git clone https://github.com/yourusername/GearCrateLite.git
cd GearCrateLite
```

---

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Python Packages

```bash
pip install -r requirements.txt
```

---

# ▶️ HOW TO RUN THE APP

## 1. Activate the virtual environment

```bash
cd GearCrateLite
source .venv/bin/activate
```

## 2. Start the Flask server

```bash
python3 app.py
```

Output example:

```
 * Running on http://127.0.0.1:5000/
```

## 3. Open GearCrate Lite in your browser

```
http://127.0.0.1:5000
```

---

## 🌐 Optional: Make the app available on your LAN

Edit the last line in `app.py`:

```python
app.run(debug=True, host="0.0.0.0")
```

Restart the app:

```bash
python3 app.py
```

Now you can access it from any device on your network:

```
http://<your-LAN-ip>:5000
```

Example:

```
http://192.168.1.50:5000
```

---

## 🗄️ Database Info

`inventory.db` is created automatically on first run.

### Reset your inventory:

```bash
rm inventory.db
python3 app.py
```

---

## 🔍 Star Citizen Wiki Autocomplete

The `/lookup` endpoint uses the **Star Citizen Wiki API** to fetch:

- Item names  
- Thumbnail images  
- Short text extracts  

Used for autocomplete fields inside the UI.

---

## 📝 Attribution

This project is a **remix of GearCrate** by KruemelGames:  
https://github.com/KruemelGames/GearCrate

GearCrate Lite is a simplified, redesigned, and Linux-focused adaptation.

---

## 🧑‍🚀 Enjoy GearCrate Lite!
