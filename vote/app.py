from flask import Flask, render_template, request, redirect, url_for
import os
import redis
import json

# Simple voting app: pushes votes into Redis for the worker to consume.
app = Flask(__name__)

# Redis connection (service name 'redis' is used inside Docker Compose)
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.route('/')
def index():
    # Render a simple voting page
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    # Get choice from form and push to Redis list 'votes'
    choice = request.form.get('choice')
    if not choice:
        return redirect(url_for('index'))

    # Create a small JSON message and push to the 'votes' list
    msg = json.dumps({'choice': choice})
    r.rpush('votes', msg)

    # Also update a fast Redis counter for live results
    r.hincrby('counts', choice, 1)

    return redirect(url_for('index'))

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    # Run on port 80 so container maps easily to host ports
    app.run(host='0.0.0.0', port=80)
