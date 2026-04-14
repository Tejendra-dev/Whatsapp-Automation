"""
send_emails.py
--------------
Reads generated_emails.csv (output of generate_emails.py).
Sends each email via Gmail SMTP with the correct resume attached.
Skips rows with status != 'ready' or missing body.
Logs results to send_log.txt.
"""

import csv
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
INPUT_CSV      = "generated_emails.csv"
LOG_FILE       = "send_log.txt"
SEND_DELAY_SEC = 3      # seconds between sends to avoid Gmail rate limit

EMAIL_USER  = os.getenv("EMAIL_USER")   # your Gmail address
EMAIL_PASS  = os.getenv("EMAIL_PASS")   # Gmail App Password (NOT your login password)
SENDER_NAME = os.getenv("SENDER_NAME", "Tejendra Ayyappa Reddy Syamala")


# ── Email sender ─────────────────────────────────────────────────────────────

def attach_resume(msg: MIMEMultipart, resume_path: str):
    """Attach a PDF file to the email."""
    if not os.path.exists(resume_path):
        print(f"  ⚠️  Resume not found: {resume_path} — sending without attachment")
        return

    with open(resume_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    filename = os.path.basename(resume_path)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)


def send_email(smtp: smtplib.SMTP_SSL, row: dict) -> bool:
    """Build and send one email. Returns True on success."""
    msg = MIMEMultipart()
    msg["From"]    = f"{SENDER_NAME} <{EMAIL_USER}>"
    msg["To"]      = row["send_to"]
    msg["Subject"] = row["subject"]

    msg.attach(MIMEText(row["body"], "plain"))
    attach_resume(msg, row["resume"])

    try:
        smtp.sendmail(EMAIL_USER, row["send_to"], msg.as_string())
        return True
    except smtplib.SMTPException as e:
        print(f"  ❌  SMTP error: {e}")
        return False


def log_result(entry: str):
    """Append a line to the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌  EMAIL_USER and EMAIL_PASS must be set in .env")
        print("    (Use a Gmail App Password — NOT your regular Gmail password)")
        print("    Generate one at: Google Account → Security → 2-Step Verification → App Passwords")
        return

    if not os.path.exists(INPUT_CSV):
        print(f"❌  '{INPUT_CSV}' not found. Run generate_emails.py first.")
        return

    with open(INPUT_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Filter only ready rows
    ready = [r for r in rows if r.get("status") == "ready" and r.get("body", "").strip()]
    skipped = len(rows) - len(ready)

    if not ready:
        print("⚠️  No emails with status='ready'. Check generated_emails.csv.")
        return

    print(f"\n📨  Preparing to send {len(ready)} email(s)  ({skipped} skipped)\n")

    # Preview before sending
    print("── PREVIEW ─────────────────────────────────────────────────")
    for i, r in enumerate(ready, 1):
        print(f"  {i}. To: {r['send_to']}  |  {r['company']} – {r['role']}")
    print("─────────────────────────────────────────────────────────────")

    confirm = input("\nSend all? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        print("Aborted.")
        return

    sent_ok    = 0
    sent_fail  = 0
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_result(f"\n=== Send run: {timestamp} ===")

    print(f"\n🚀  Connecting to Gmail SMTP...\n")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            print("  ✅  Logged in to Gmail\n")

            for i, row in enumerate(ready, 1):
                print(f"  [{i}/{len(ready)}] → {row['send_to']}  ({row['company']} | {row['role']})")

                success = send_email(smtp, row)

                if success:
                    print(f"         ✅  Sent  |  Resume: {row['resume']}")
                    log_result(f"SENT     | {row['send_to']} | {row['company']} | {row['role']}")
                    sent_ok += 1
                else:
                    log_result(f"FAILED   | {row['send_to']} | {row['company']} | {row['role']}")
                    sent_fail += 1

                if i < len(ready):
                    print(f"         ⏳ Waiting {SEND_DELAY_SEC}s...")
                    time.sleep(SEND_DELAY_SEC)

    except smtplib.SMTPAuthenticationError:
        print("\n❌  Gmail auth failed.")
        print("   → Make sure EMAIL_PASS is an App Password (not your Gmail login).")
        print("   → Enable 2-FA then generate: Google Account → Security → App Passwords")
        return
    except Exception as e:
        print(f"\n❌  Unexpected error: {e}")
        return

    print(f"\n{'─'*60}")
    print(f"  ✅  Sent:   {sent_ok}")
    print(f"  ❌  Failed: {sent_fail}")
    print(f"  📋  Log saved to '{LOG_FILE}'")


if __name__ == "__main__":
    main()
