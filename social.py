from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash
from supabase import Client, create_client

app = Flask(__name__)
# 🔑 Supabase credentials
url = "https://mmgvxtxbciwlqygwayie.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tZ3Z4dHhiY2l3bHF5Z3dheWllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDE2MTU1MywiZXhwIjoyMDg5NzM3NTUzfQ.tz-hEF-puFeEiA8ljYj3lwSBadBGlduxnI46QvhCo0w"

supabase: Client = create_client(url, key)
@app.route("/")
def home():
    return "Supabase Connected!"

@app.route("/users", methods=["GET"])
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


@app.route("/users/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    required_fields = ["name", "username", "email", "password"]
    missing = False
    for f in required_fields:
        if not data.get(f):
            missing = True
            break
    if missing:
        return jsonify({"error": "Missing required fields"}), 400

    # Validate lengths
    if len(data["username"]) > 10:
        return jsonify({"error": "Username must be 10 characters or less"}), 400
    if len(data["email"]) > 50:
        return jsonify({"error": "Email must be 50 characters or less"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # check duplicates
    user_by_username = supabase.table("users").select("id").eq("username", data["username"]).limit(1).execute()
    if user_by_username.data:
        return jsonify({"error": "Username already in use"}), 409

    user_by_email = supabase.table("users").select("id").eq("email", data["email"]).limit(1).execute()
    if user_by_email.data:
        return jsonify({"error": "Email already in use"}), 409

    hashed_password = generate_password_hash(data["password"])
    record = {
        "name": data["name"],
        "username": data["username"],
        "email": data["email"],
        "bio": data.get("bio", ""),
        "password": hashed_password,
    }

    inserted = supabase.table("users").insert(record).execute()

    return jsonify({"message": "User created successfully!", "user": inserted.data}), 201
@app.route("/users/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    # Validate input
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    # Fetch user
    response = supabase.table("users") \
        .select("*") \
        .eq("email", data["email"]) \
        .limit(1) \
        .execute()

    if not response.data:
        return jsonify({"error": "User not found"}), 404

    user = response.data[0]

    # Verify password
    if not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"]
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True)