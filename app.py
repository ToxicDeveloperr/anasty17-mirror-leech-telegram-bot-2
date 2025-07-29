from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Tech VJ"

if __name__ == "__main__":
    # Development server fallback (not used by Gunicorn in production)
    app.run(host="0.0.0.0", port=8080)
