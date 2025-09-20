from flask import Flask, jsonify, request
from threading import Thread
import time

app = Flask(__name__)

# Dummy state variables (replace with calls to your real backend logic)
chanting_active = False
chant_start_time = None

@app.route('/start', methods=['POST'])
def start_chant():
    global chanting_active, chant_start_time
    chanting_active = True
    chant_start_time = time.time()
    # Call your backend start chanting logic here
    return jsonify({"status": "chanting started"})

@app.route('/stop', methods=['POST'])
def stop_chant():
    global chanting_active, chant_start_time
    chanting_active = False
    duration = time.time() - chant_start_time if chant_start_time else 0
    chant_start_time = None
    # Call your backend stop chanting logic here and get duration
    return jsonify({"status": "chanting stopped", "duration": duration})

@app.route('/status', methods=['GET'])
def get_status():
    # For demo, return dummy statuses, replace with real backend info
    status = {
        "chanting": chanting_active,
        "duration": time.time() - chant_start_time if chanting_active else 0,
        "posture": "Good",
        "eyes": "Open"
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)