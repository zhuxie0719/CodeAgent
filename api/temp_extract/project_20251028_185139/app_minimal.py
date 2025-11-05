"""
Minimal Flask 2.0.0 Test Application
Simple test to verify Flask installation and basic functionality
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    """Main route"""
    return jsonify({
        "message": "Flask 2.0.0 Test Application",
        "status": "running",
        "version": "2.0.0"
    })

@app.route('/test')
def test():
    """Test route"""
    return jsonify({"test": "success"})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
