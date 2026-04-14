"""
parse_jobs.py
-------------
Paste WhatsApp job messages into raw_jobs.txt.
Posts are split on the 'FREE REFERRAL ALERT' header line.
"""

import re
import csv
import os

INPUT_FILE  = "raw_jobs.txt"
OUTPUT_FILE = "jobs.csv"

def clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[\•\-\*\>\→\–\►]+\s*", "", text)
    return text.strip()

def extract_field(block: str, label_pattern: str) -> str:
    m = re.search(label_pattern, block, re.IGNORECASE)
    if m:
        return clean(m.group(1))
    return ""

def extract_email(block: str) -> str:
    m = re.search(r"(?:Send your resume|resume|📩)[^\n]*?([\w.\-+]+@[\w.\-]+\.[a-zA-Z]{2,})", block, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"[\w.\-+]+@[\w.\-]+\.[a-zA-Z]{2,}", block)
    if m:
        return m.group(0).strip()
    return ""

def extract_skills(block: str) -> str:
    m = re.search(
        r"(?:⚙️\s*Skills?|Skills?)\s*[:\-]?\s*\n((?:[ \t]*[•\-\*►]?.+\n?)+)",
        block, re.IGNORECASE
    )
    if m:
        lines = [clean(l) for l in m.group(1).splitlines() if clean(l)]
        skills = []
        for l in lines:
            if re.match(r"^[📩📌🚨🔥🏢👤📍🎓💰]", l):
                break
            skills.append(l)
        if skills:
            return ", ".join(skills)
    m = re.search(r"(?:⚙️\s*Skills?|Skills?)\s*[:\-]\s*(.+)", block, re.IGNORECASE)
    if m:
        return clean(m.group(1))
    return ""

def parse_blocks(raw: str) -> list:
    blocks = re.split(r"🚨[🔥\s]*FREE REFERRAL ALERT[🔥\s]*🚨", raw)
    jobs = []
    seen_emails = set()

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        email = extract_email(block)
        if not email:
            continue
        if email.lower() in seen_emails:
            print(f"  ⏭️   Duplicate skipped: {email}")
            continue
        seen_emails.add(email.lower())

        company  = extract_field(block, r"🏢\s*Company\s*[:\-]\s*(.+)") or extract_field(block, r"Company\s*[:\-]\s*(.+)")
        role     = extract_field(block, r"👤\s*Role\s*[:\-]\s*(.+)")     or extract_field(block, r"Role\s*[:\-]\s*(.+)")
        location = extract_field(block, r"📍[^\n]*?[:\-]?\s*(.+)")
        batch    = extract_field(block, r"🎓[^\n]*?[:\-]?\s*(.+)")
        stipend  = extract_field(block, r"💰[^\n]*?[:\-]?\s*(.+)")
        skills   = extract_skills(block)

        job = {
            "company":  company  or "Unknown Company",
            "role":     role     or "Unknown Role",
            "email":    email,
            "location": location or "",
            "skills":   skills,
            "batch":    batch    or "",
            "stipend":  stipend  or "",
        }
        jobs.append(job)
        print(f"  ✅  {job['company']:<40} | {job['role']:<45} | {job['email']}")

    return jobs

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌  '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        raw = f.read()

    print(f"\n📋  Parsing '{INPUT_FILE}' ...\n")
    jobs = parse_blocks(raw)

    if not jobs:
        print("\n⚠️  No valid posts found.")
        return

    fieldnames = ["company", "role", "email", "location", "skills", "batch", "stipend"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

    print(f"\n✅  Saved {len(jobs)} unique job(s) to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
