#!/usr/bin/env python3
"""
Sends a deployment notification email over SMTP.
Reads credentials from env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.
Usage: notify-email.py --to a@x.com,b@x.com --status success --app MyApp \
                        --env production --version 1.4.0 --run-url https://...
"""
import argparse
import os
import smtplib
import ssl
import sys
from email.mime.text import MIMEText


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True, help="comma-separated recipient list")
    p.add_argument("--status", required=True, choices=["success", "failure"])
    p.add_argument("--app", required=True)
    p.add_argument("--env", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--run-url", default="")
    args = p.parse_args()

    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")

    if not all([host, user, password]):
        print("ERROR: SMTP_HOST, SMTP_USER, SMTP_PASS must be set", file=sys.stderr)
        return 1

    subject = f"[{args.status.upper()}] {args.app} → {args.env} ({args.version})"
    body = (
        f"Deployment status: {args.status}\n"
        f"App: {args.app}\n"
        f"Environment: {args.env}\n"
        f"Version: {args.version}\n"
        f"Run: {args.run_url}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = args.to

    recipients = [r.strip() for r in args.to.split(",") if r.strip()]

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(user, password)
        server.sendmail(user, recipients, msg.as_string())

    print(f"Email notification sent to {', '.join(recipients)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
