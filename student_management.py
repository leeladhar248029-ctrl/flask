from flask import Flask, jsonify, request
from supabase import Client, create_client

app = Flask(__name__)

# Supabase Connection
url = "https://qojjkgyidudxswrjxukj.supabase.co/rest/v1/"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvamprZ3lpZHVkeHN3cmp4dWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1MTYwMTgsImV4cCI6MjA5NjA5MjAxOH0.8FT46nAqlUPDQGqqcKOw1muRjP9WZpBfZS5qKLWkNhM"

supabase = create_client(url, key)

# Home
@app.route("/")
def home():
    return "Student Management API"

# Get All Students
@app.route("/students", methods=["GET"])
def get_students():
    response = supabase.table("students").select("*").execute()
    return jsonify(response.data)

# Add Student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    student = {
        "id": data["id"],
        "name": data["name"],
        "email": data["email"],
        "age": data["age"],
        "course": data["course"],
        "phone_number": data["phone_number"],
        "address": data["address"],
        "gender": data["gender"],
        "current_year": data["current_year"],
        "roll_number": data["roll_number"],
        "city": data["city"],
        "state": data["state"]
    }

    response = supabase.table("students").insert(student).execute()

    return jsonify(response.data)

# Update Student
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json()

    response = (
        supabase.table("students")
        .update(data)
        .eq("id", id)
        .execute()
    )

    return jsonify(response.data)

# Delete Student
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    response = (
        supabase.table("students")
        .delete()
        .eq("id", id)
        .execute()
    )

    return jsonify({"message": "Student Deleted"})

if __name__ == "__main__":
    app.run(debug=True)