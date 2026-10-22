#!/bin/bash
unset GOOGLE_CLOUD_QUOTA_PROJECT
uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 19001 > uvicorn.log 2>&1 &
SERVER_PID=$!
sleep 5
agents-cli eval run --url http://127.0.0.1:19001 --app-name app
kill -9 $SERVER_PID
