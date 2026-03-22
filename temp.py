from flask import Flask, jsonify, request
from supabase import create_client, Client

app = Flask(__name__)

# 🔑 Supabase credentials
url = "https://qnpooqplearvdxxmpqfp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFucG9vcXBsZWFydmR4eG1wcWZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQxNTAyMjAsImV4cCI6MjA4OTcyNjIyMH0.MRPxcadT6YrawfgIboLh7jCyWzykR3SICM8yPaiB8BA"

supabase: Client = create_client(url, key)

@app.route("/")
def home():
    return "Supabase Connected!"

@app.route("/users", methods=["GET"])
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    response = supabase.table("users").insert(data).execute()
    return jsonify({"message": "User added", "data": response.data}), 201

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    response = supabase.table("users").update(data).eq("id", user_id).execute()
    if not response.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated", "data": response.data})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    response = supabase.table("users").delete().eq("id", user_id).execute()
    if not response.data:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"})

if __name__ == "__main__":
    app.run(debug=True)