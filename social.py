from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return "Supabase Connected!"

@app.route("/ff")
def homeff():
    return "Supabase Conffffffnected!"


if __name__ == "__main__":
    app.run(debug=True)