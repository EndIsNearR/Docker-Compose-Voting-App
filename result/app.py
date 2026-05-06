from flask import Flask, render_template, jsonify
import os
import pg8000

app = Flask(__name__)

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'smartvdb')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'smartv')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'smartvpass')


def get_db_connection():
    # Open a fresh connection for each request so the app stays simple.
    return pg8000.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )

@app.route('/')
def index():
    # Page shows live results via JS polling
    return render_template('index.html')

@app.route('/results')
def results():
    # Read the vote totals from PostgreSQL and return them as JSON.
    query = """
        SELECT choice, COUNT(*) AS total
        FROM votes
        GROUP BY choice
    """

    counts = {'Cats': 0, 'Dogs': 0}

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)

        for choice, total in cur.fetchall():
            counts[choice] = int(total)

        cur.close()
        conn.close()
    except Exception as error:
        # If the DB is still starting up, return zeros so the page still loads.
        print(f'Failed to read results from database: {error}')

    return jsonify(counts)

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
