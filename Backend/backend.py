from flask import Flask, jsonify
import random
import time
import os

app = Flask(__name__)

# Configuration for simulating failures
FAILURE_RATE = float(os.getenv('FAILURE_RATE', '0.3'))
DELAY_RATE = float(os.getenv('DELAY_RATE', '0.2'))

@app.route('/api/data', methods=['GET'])
def get_data():
    # Simulate random delays
    if random.random() < DELAY_RATE:
        time.sleep(5)  # 5 second delay
    
    # Simulate random failures
    if random.random() < FAILURE_RATE:
        return jsonify({'error': 'Internal Server Error'}), 500
    
    return jsonify({'data': 'Success!', 'timestamp': time.time()}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({'status': 'ready'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)