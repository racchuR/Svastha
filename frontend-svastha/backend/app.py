from svastha import OmChantingGuide
from flask import Flask, jsonify, request
from threading import Thread
import time

app = Flask(__name__)

guide = OmChantingGuide()
thread = Thread(target=guide.run, daemon=True)
thread.start()

@app.route('/start', methods=['POST'])
def start_chant():
    guide.start_chant()  # Call backend start chanting
    return jsonify({"status": "chanting started"})

@app.route('/stop', methods=['POST'])
def stop_chant():
    duration = guide.end_chant()  # Call backend stop chanting and get duration
    return jsonify({"status": "chanting stopped", "duration": duration})
    
@app.route('/status', methods=['GET'])
def get_status():
    status = guide.get_status()  # Get real-time status from backend
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
