from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is running!"

@app.route('/api')
def api():
    return {"message": "API is working"}

if __name__ == '__main__':
    app.run(debug=True)