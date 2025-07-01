#!/usr/bin/env python3
"""
Simple test for post generation without complex dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test basic imports
try:
    from flask import Flask
    print("✅ Flask import successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

try:
    import openai
    print("✅ OpenAI import successful")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")
    sys.exit(1)

# Test Flask app creation
try:
    app = Flask(__name__)
    print("✅ Flask app creation successful")
except Exception as e:
    print(f"❌ Flask app creation failed: {e}")
    sys.exit(1)

# Test with a simple endpoint
@app.route("/api/health")
def health():
    return {"status": "healthy", "message": "Simple backend is working!"}

@app.route("/api/test-openai")
def test_openai():
    # Check if OpenAI can be initialized
    try:
        # Using a dummy key to test initialization
        client = openai.OpenAI(api_key="test-key")
        return {"status": "openai_client_created", "message": "OpenAI client can be initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🚀 Starting simple Flask server...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}") 