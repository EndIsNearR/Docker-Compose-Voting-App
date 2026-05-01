import os
import time
import json
import redis
import psycopg2

# Worker: consumes votes from Redis list 'votes' and saves them into Postgres.

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'smartvdb')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'smartv')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'smartvpass')

def connect_db():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    conn.autocommit = True
    return conn

def main():
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    print('Worker started, connecting to DB...')
    # Try to connect to DB, retry until available
    while True:
        try:
            conn = connect_db()
            break
        except Exception as e:
            print('Waiting for DB...', e)
            time.sleep(2)

    cur = conn.cursor()

    print('Connected. Waiting for votes in Redis list "votes"...')
    # Blocking pop from 'votes' list
    while True:
        try:
            item = r.blpop('votes', timeout=0)  # returns (list_name, value)
            if not item:
                continue
            _, msg = item
            data = json.loads(msg)
            choice = data.get('choice')
            if choice:
                # Insert into votes table
                cur.execute("INSERT INTO votes (choice) VALUES (%s)", (choice,))
                print(f"Saved vote: {choice}")
        except Exception as e:
            print('Worker error, retrying...', e)
            time.sleep(1)

if __name__ == '__main__':
    main()
