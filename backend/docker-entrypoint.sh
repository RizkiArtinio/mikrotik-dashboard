#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
# Must be a single worker process: the router-polling scheduler and the
# WebSocket connection registry both live in-process (app/scheduler,
# app/websocket/connection_manager.py). Multiple worker processes would each
# run their own scheduler (duplicate router polls, duplicate DB seeding) and
# only broadcast to whichever worker a given client happened to connect to.
# Scale horizontally later by moving that state to Redis pub/sub, not by
# raising --workers here.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
