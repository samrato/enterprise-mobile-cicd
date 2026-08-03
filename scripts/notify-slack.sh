#!/usr/bin/env bash
# Posts a formatted deployment notification to a Slack Incoming Webhook.
# Usage: notify-slack.sh <webhook-url> <status:success|failure> <app> <env> <version> <run-url>
set -euo pipefail
WEBHOOK="${1:?webhook url required}"
STATUS="${2:?status required}"
APP="${3:-app}"
ENVIRONMENT="${4:-unknown}"
VERSION="${5:-unknown}"
RUN_URL="${6:-}"

COLOR="#36a64f"
EMOJI=":white_check_mark:"
if [[ "$STATUS" != "success" ]]; then
  COLOR="#e01e5a"
  EMOJI=":x:"
fi

PAYLOAD=$(cat << JSON
{
  "attachments": [
    {
      "color": "${COLOR}",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "${EMOJI} *${APP}* deployment to *${ENVIRONMENT}* — \`${VERSION}\`\n<${RUN_URL}|View run>"
          }
        }
      ]
    }
  ]
}
JSON
)

curl -sf -X POST -H 'Content-type: application/json' --data "$PAYLOAD" "$WEBHOOK" > /dev/null
echo "Slack notification sent."
