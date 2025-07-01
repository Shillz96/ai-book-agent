from flask import Flask, jsonify
from flask_cors import CORS
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return jsonify({
        "message": "Test Flask App is running!",
        "status": "ok"
    })

if __name__ == "__main__":
    logger.info("Starting test Flask application...")
    app.run(host="0.0.0.0", port=5000, debug=True) 