from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # allows the frontend (on a different port/IP) to call this API

# Change DB_PATH via environment variable if needed. Defaults to a local
# "data" folder next to this file - works the same on EC2 or your laptop.
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "items.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


BACKEND_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Flask Backend - Saved Data</title>
<meta http-equiv="refresh" content="5" />
<style>
  body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
         background:#0f172a; color:#e2e8f0; margin:0; padding:32px 16px; }
  .container { max-width: 700px; margin: 0 auto; }
  h1 { font-size: 1.4rem; margin-bottom: 4px; }
  p.sub { color:#94a3b8; margin-top:0; }
  table { width:100%; border-collapse: collapse; margin-top: 20px; }
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #334155; font-size:0.9rem; }
  th { color:#94a3b8; font-weight:600; }
  .badge { background:#1e293b; padding:2px 8px; border-radius:6px; font-size:0.75rem; color:#94a3b8; }
  .empty { color:#64748b; margin-top:20px; }
</style>
</head>
<body>
  <div class="container">
    <h1>Flask Backend &mdash; Saved Data</h1>
    <p class="sub">Data submitted from the frontend shows up here too. Auto-refreshes every 5s.</p>
    {% if items %}
    <table>
      <tr><th>ID</th><th>Name</th><th>Message</th><th>Created At</th></tr>
      {% for it in items %}
      <tr>
        <td><span class="badge">#{{ it.id }}</span></td>
        <td>{{ it.name }}</td>
        <td>{{ it.message }}</td>
        <td>{{ it.created_at }}</td>
      </tr>
      {% endfor %}
    </table>
    {% else %}
    <p class="empty">No data saved yet. Submit the form on the frontend or POST to /api/items.</p>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    rows = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(BACKEND_PAGE, items=[dict(r) for r in rows])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/items", methods=["GET"])
def get_items():
    conn = get_db()
    rows = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True, silent=True) or {}
    name = str(data.get("name", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not message:
        return jsonify({"error": "name and message are required"}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO items (name, message) VALUES (?, ?)", (name, message)
    )
    conn.commit()
    new_id = cur.lastrowid
    row = conn.execute("SELECT * FROM items WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": item_id}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # 0.0.0.0 = reachable from any IP (needed for EC2), not just localhost
    app.run(host="0.0.0.0", port=port)
