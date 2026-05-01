from flask import Flask, render_template, jsonify
import os
import redis

app = Flask(__name__)

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.route('/')
def index():
    # Page shows live results via JS polling
    return render_template('index.html')

@app.route('/results')
def results():
    # Return the Redis stored counts as JSON
    counts = r.hgetall('counts') or {}
    # Ensure numeric values
    out = {k: int(v) if v is not None else 0 for k, v in counts.items()}
    return jsonify(out)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
