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
    return "sdfsDse!"

@app.route("/users", methods=["GET"])
def get_users():
    response = supabase.table("users").select("*").execute()
    return jsonify(response.data)


@app.route("/users/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    required_fields = ["name", "email", "password"]
    missing = False
    for f in required_fields:
        if not data.get(f):
            missing = True
            break
    if missing:
        return jsonify({"error": "Missing required fields"}), 400

    if len(data["email"]) > 50:
        return jsonify({"error": "Email must be 50 characters or less"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400


    user_by_email = supabase.table("users").select("id").eq("email", data["email"]).limit(1).execute()
    if user_by_email.data:
        return jsonify({"error": "Email already in use"}), 409

    hashed_password = generate_password_hash(data["password"])
    record = {
        "name": data["name"],
        "email": data["email"],
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


# create table public.users (
#   id serial not null,
#   name character varying(20) not null,
#   email character varying(100) null,
#   password character varying(255) null,
#   followers integer[] null,
#   followings integer[] null,
#   constraint users_pkey primary key (id),
#   constraint unique_email unique (email)
# ) TABLESPACE pg_default;

@app.route("/follow", methods=["PUT"])
def follow():
    data = request.get_json() or {}

    required_fields = ["follower_id", "followee_id"]
    missing = False
    for f in required_fields:
        if not data.get(f):
            missing = True
            break
    if missing:
        return jsonify({"error": "Missing required fields"}), 400
    
    # if user id is not found, return error
    follower_response = supabase.table("users").select("id").eq("id", data["follower_id"]).limit(1).execute()
    if not follower_response.data:
        return jsonify({"error": "Follower user not found"}), 404

    followee_response = supabase.table("users").select("id").eq("id", data["followee_id"]).limit(1).execute()
    if not followee_response.data:
        return jsonify({"error": "Followee user not found"}), 404

    # follwer_id should not be same as followee_id
    if data["follower_id"] == data["followee_id"]:
        return jsonify({"error": "User cannot follow themselves"}), 400
    
    # if already following, return error
    if data["followee_id"] in follower_response.data[0].get("followings", []):
        return jsonify({"error": "Already following this user"}), 400
    
    # update follower's followings
    updated_followings = (follower_response.data[0].get("followings", []) + [data["followee_id"]])
    supabase.table("users").update({"followings": updated_followings}).eq("id", data["follower_id"]).execute()

    # update followee's followers
    updated_followers = (followee_response.data[0].get("followers", []) + [data["follower_id"]])
    supabase.table("users").update({"followers": updated_followers}).eq("id", data["followee_id"]).execute()

    return jsonify({"message": "Followed successfully!"}), 200

@app.route("/unfollow", methods=["PUT"])
def unfollow():
    data = request.get_json() or {}

    required_fields = ["follower_id", "followee_id"]
    missing = False
    for f in required_fields:
        if not data.get(f):
            missing = True
            break
    if missing:
        return jsonify({"error": "Missing required fields"}), 400

    # if user id is not found, return error
    follower_response = supabase.table("users").select("id").eq("id", data["follower_id"]).limit(1).execute()
    if not follower_response.data:
        return jsonify({"error": "Follower user not found"}), 404

    followee_response = supabase.table("users").select("id").eq("id", data["followee_id"]).limit(1).execute()
    if not followee_response.data:
        return jsonify({"error": "Followee user not found"}), 404

    # if not following, return error
    if data["followee_id"] not in follower_response.data[0].get("followings", []):
        return jsonify({"error": "Not following this user"}), 400

    # update follower's followings
    updated_followings = [id for id in follower_response.data[0].get("followings", []) if id != data["followee_id"]]
    supabase.table("users").update({"followings": updated_followings}).eq("id", data["follower_id"]).execute()

    # update followee's followers
    updated_followers = [id for id in followee_response.data[0].get("followers", []) if id != data["follower_id"]]
    supabase.table("users").update({"followers": updated_followers}).eq("id", data["followee_id"]).execute()

    return jsonify({"message": "Unfollowed successfully!"}), 200


if __name__ == "__main__":
    app.run(debug=True)