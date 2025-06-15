#!/bin/bash

LOG_FILE="/var/log/ns_keepalive.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Load .env
source /root/nationstates/.env || {
  echo "[$TIMESTAMP] ERROR: Failed to load .env file" >> "$LOG_FILE"
  exit 1
}

# Authenticate and capture HTTP response
HTTP_RESPONSE=$(curl -i \
  -H "X-Autologin: $AUTOLOGIN" \
  -A "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0" \
  "$URL" 2>&1)

CURL_EXIT=$?

# Extract status code from response headers
HTTP_STATUS=$(echo "$HTTP_RESPONSE" | grep -oP 'HTTP/\d\.?\d?\s+\K\d{3}' | head -n 1)

# Handle errors
if [ $CURL_EXIT -ne 0 ]; then
  echo "[$TIMESTAMP] ERROR: Curl failed with exit code $CURL_EXIT" >> "$LOG_FILE"
  exit 1
fi

if [ -z "$HTTP_STATUS" ]; then
  echo "[$TIMESTAMP] ERROR: Failed to extract HTTP status from response" >> "$LOG_FILE"
  echo "DEBUG: Full response:\n$HTTP_RESPONSE" >> "$LOG_FILE"  # Debugging aid
  exit 1
fi

# Process XML response and truncate
HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed -n '/^\r$/,$p' | sed '1d')
TRUNCATED_BODY=$(echo "$HTTP_BODY" | tr -d '\n' | tr -s ' ' | cut -c 1-100)

# Log results
if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 300 ]; then
  echo "[$TIMESTAMP] SUCCESS: HTTP $HTTP_STATUS | Response: ${TRUNCATED_BODY}..." >> "$LOG_FILE"
else
  echo "[$TIMESTAMP] FAILED: HTTP $HTTP_STATUS | Response: ${TRUNCATED_BODY}..." >> "$LOG_FILE"
fi

