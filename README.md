# Smart Voting App (Docker Compose)

Simple beginner-friendly multi-container app demonstrating a small voting system.

Architecture:
- Frontend Layer: `vote/` — Flask app where users vote (port 8080)
- Processing Layer: `worker/` — Python worker consumes votes from Redis and writes to Postgres
- Data Layer: `db` — PostgreSQL (volume persisted)
- Cache/Queue Layer: `redis` — Redis used as queue and live counts

Docker networks:
- `frontend` — user-facing services (`vote`, `result`)
- `backend` — internal services (`worker`, `redis`, `db`)
- `vote` and `result` join both networks so they can still reach Redis on the backend network while staying exposed only on the frontend side.

Folders and key files:
- `docker-compose.yml` — Compose file wiring services together.
- `vote/` — Flask vote app (Dockerfile, `app.py`, template).
- `result/` — Flask result app showing live counts (Dockerfile, `app.py`, template).
- `worker/` — Simple Python worker (Dockerfile, `app.py`).
- `db/init.sql` — SQL to create the `votes` table on DB init.

How containers talk to each other
- `vote` pushes JSON messages onto Redis list `votes` and increments Redis hash `counts`.
- `worker` uses `BLPOP votes` on Redis to consume votes and inserts rows into Postgres.
- `result` reads Redis hash `counts` to show live counts (fast) and updates in the DB are the canonical history.
- Docker Compose provides an internal network; services use service names (`redis`, `db`) as hostnames.
- Docker Compose now uses two named networks, and the apps reach Redis and Postgres through Docker DNS hostnames.

Run locally
1. From this folder run:

```bash
docker compose up --build
```

2. Open the vote UI: http://localhost:8080
3. Open the results UI: http://localhost:8081

Notes for presentation
- Explain that Redis is used as a lightweight queue (list) and a fast cache (hash).
- The worker decouples web requests from DB writes — this is common in production.
- The `db` volume keeps votes even after containers stop.
- The frontend network is for browser-facing apps, while the backend network keeps the queue and database private.
