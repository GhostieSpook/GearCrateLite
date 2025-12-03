import sqlite3
from pathlib import Path
from urllib.parse import quote

import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    jsonify,
)

app = Flask(__name__)

DB_PATH = Path("inventory.db")


def get_db():
    """Open a SQLite connection with dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create items table if it doesn't exist (includes image_url)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            location TEXT,
            notes TEXT,
            image_url TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items ORDER BY name COLLATE NOCASE")
    items = cur.fetchall()
    conn.close()
    return render_template("index.html", items=items)


@app.route("/add", methods=["POST"])
def add_item():
    """Add a new item OR merge with an existing matching one."""
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip() or None
    quantity = request.form.get("quantity") or "1"
    location = (request.form.get("location") or "").strip() or None
    notes = (request.form.get("notes") or "").strip() or None
    image_url = (request.form.get("image_url") or "").strip() or None

    if not name:
        return redirect(url_for("index"))

    try:
        qty = int(quantity)
    except ValueError:
        qty = 1

    conn = get_db()
    cur = conn.cursor()

    # Merge logic: same name (case-insensitive) + same category + same location
    cur.execute(
        """
        SELECT id, quantity
        FROM items
        WHERE name = ? COLLATE NOCASE
          AND IFNULL(category, '') = IFNULL(?, '')
          AND IFNULL(location, '') = IFNULL(?, '')
        """,
        (name, category or "", location or ""),
    )
    existing = cur.fetchone()

    if existing:
        new_qty = (existing["quantity"] or 0) + qty
        cur.execute(
            """
            UPDATE items
            SET quantity = ?, notes = COALESCE(?, notes), image_url = COALESCE(?, image_url)
            WHERE id = ?
            """,
            (new_qty, notes, image_url, existing["id"]),
        )
    else:
        cur.execute(
            """
            INSERT INTO items (name, category, quantity, location, notes, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, category, qty, location, notes, image_url),
        )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/item/<int:item_id>/edit", methods=["GET"])
def edit_item(item_id):
    """Show edit form for a single item."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cur.fetchone()
    conn.close()

    if not item:
        abort(404)

    return render_template("edit_item.html", item=item)


@app.route("/item/<int:item_id>/update", methods=["POST"])
def update_item(item_id):
    """Save changes from the edit form."""
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip() or None
    quantity = request.form.get("quantity") or "1"
    location = (request.form.get("location") or "").strip() or None
    notes = (request.form.get("notes") or "").strip() or None
    image_url = (request.form.get("image_url") or "").strip() or None

    if not name:
        return redirect(url_for("index"))

    try:
        qty = int(quantity)
    except ValueError:
        qty = 1

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE items
        SET name = ?, category = ?, quantity = ?, location = ?, notes = ?, image_url = ?
        WHERE id = ?
        """,
        (name, category, qty, location, notes, image_url, item_id),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/item/<int:item_id>", methods=["GET"])
def view_item(item_id):
    """Detail view for a single item (full notes, wiki link, etc.)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cur.fetchone()
    conn.close()

    if not item:
        abort(404)

    wiki_url = None
    name = item["name"]
    if name:
        # Build a basic Star Citizen Wiki URL from the title
        wiki_url = "https://starcitizen.tools/" + quote(name.replace(" ", "_"))

    return render_template("view_item.html", item=item, wiki_url=wiki_url)


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/lookup")
def lookup():
    """
    Autocomplete endpoint.

    Uses Star Citizen Wiki's MediaWiki API 'prefixsearch' to suggest item titles
    and, where possible, a thumbnail image URL + short description.
    """
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify([])

    try:
        # 1) Get matching page titles
        resp = requests.get(
            "https://starcitizen.tools/api.php",
            params={
                "action": "query",
                "list": "prefixsearch",
                "pssearch": q,
                "pslimit": 10,
                "psnamespace": 0,
                "format": "json",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return jsonify([])

    titles = [
        item.get("title")
        for item in data.get("query", {}).get("prefixsearch", [])
        if item.get("title")
    ]
    if not titles:
        return jsonify([])

    thumb_map: dict[str, str] = {}
    extract_map: dict[str, str] = {}

    try:
        # 2) Ask for thumbnails + short text extracts for those titles
        resp2 = requests.get(
            "https://starcitizen.tools/api.php",
            params={
                "action": "query",
                "prop": "pageimages|extracts",
                "piprop": "thumbnail",
                "pithumbsize": 512,
                "titles": "|".join(titles),
                "exintro": 1,
                "explaintext": 1,
                "exsentences": 2,
                "format": "json",
            },
            timeout=5,
        )
        resp2.raise_for_status()
        data2 = resp2.json()
        for page in data2.get("query", {}).get("pages", {}).values():
            title = page.get("title")
            if not title:
                continue
            thumb = page.get("thumbnail", {}).get("source")
            extract = page.get("extract")
            if thumb:
                thumb_map[title] = thumb
            if extract:
                extract_map[title] = extract.strip()
    except Exception:
        # If this fails, we still return basic title-only results
        pass

    results = []
    for title in titles:
        results.append(
            {
                "title": title,
                "image_url": thumb_map.get(title),      # may be None
                "description": extract_map.get(title),  # may be None
            }
        )

    return jsonify(results)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
