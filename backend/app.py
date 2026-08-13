from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow requests from the Express frontend (different origin/port)

# simple in-memory store just so we have something to show back
submissions = []


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Flask backend is running.",
        "endpoints": {
            "/submit": "POST - submit form data (name, email, message)",
            "/submissions": "GET - list all submissions received so far"
        }
    })


@app.route("/submit", methods=["POST"])
def submit():
    # works whether the frontend sends JSON (fetch) or an urlencoded form post
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    errors = []
    if not name:
        errors.append("Name is required.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")
    if not message:
        errors.append("Message is required.")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    record = {"name": name, "email": email, "message": message}
    submissions.append(record)

    return jsonify({
        "success": True,
        "message": f"Thanks {name}, your submission was received by the Flask backend!",
        "data": record
    }), 200


@app.route("/submissions", methods=["GET"])
def get_submissions():
    return jsonify({"count": len(submissions), "submissions": submissions})


if __name__ == "__main__":
    # 0.0.0.0 so it's reachable from outside the container
    app.run(host="0.0.0.0", port=5000, debug=True)
