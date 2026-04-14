"""
generate_emails.py
------------------
Reads jobs.csv (output of parse_jobs.py).
For each job, picks the right resume and generates a personalized cold email
via Groq API, then saves everything to generated_emails.csv.
"""

import csv
import os
import time
import re
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
INPUT_CSV       = "jobs.csv"
OUTPUT_CSV      = "generated_emails.csv"
GROQ_MODEL      = "llama-3.1-8b-instant"
API_DELAY_SEC   = 6           # avoid Groq free-tier rate limit

# Resume files (place in same folder as this script)
RESUME_AI       = "Tejendra_resume.pdf"          # AI / ML / Prompt roles
RESUME_DEV      = "Tejendra_Ayyappa_Reddy_resume.pdf"  # Java / Web / Full Stack

# Keywords that trigger AI resume
AI_KEYWORDS = [
    "ai", "ml", "machine learning", "deep learning", "llm", "nlp",
    "prompt", "generative", "data science", "artificial intelligence",
    "ai engineer", "ai developer", "ai intern",
]

# Your personal details (also loaded from .env for privacy)
SENDER_NAME     = os.getenv("SENDER_NAME",  "Tejendra Ayyappa Reddy Syamala")
SENDER_EMAIL    = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SENDER_PHONE    = os.getenv("SENDER_PHONE", "+91-XXXXXXXXXX")
SENDER_LINKEDIN = os.getenv("SENDER_LINKEDIN", "https://linkedin.com/in/your-profile")
SENDER_GITHUB   = os.getenv("SENDER_GITHUB",   "https://github.com/your-profile")

# ── Helpers ──────────────────────────────────────────────────────────────────

def read_pdf(path: str) -> str:
    """Extract text from a PDF resume."""
    try:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"  ⚠️  Could not read {path}: {e}")
        return ""


def pick_resume(role: str) -> str:
    """Return the correct resume filename based on the role."""
    role_lower = role.lower()
    for kw in AI_KEYWORDS:
        if kw in role_lower:
            return RESUME_AI
    return RESUME_DEV


def first_name(recruiter_email: str) -> str:
    """
    We don't have the recruiter's name from WhatsApp posts — only email.
    Try to extract a first name from the email local part (e.g. shivani@ → Shivani).
    Falls back to 'Hiring Manager'.
    """
    local = recruiter_email.split("@")[0]
    # Remove numbers and dots, take first segment
    parts = re.split(r"[.\-_]", local)
    name = parts[0].capitalize() if parts else ""
    # Reject obvious non-names
    if len(name) < 3 or name.lower() in ("hr", "jobs", "careers", "info", "contact", "recruit"):
        return "Hiring Manager"
    return name


def generate_subject(role: str, company: str) -> str:
    return f"Application for {role} Role – {SENDER_NAME.split()[0]} | B.E. CSE (Data Science)"


def generate_email_body(
    client: Groq,
    resume_text: str,
    role: str,
    company: str,
    recruiter: str,
    skills: str,
    location: str,
) -> str:
    prompt = f"""
You are helping {SENDER_NAME} write a professional cold outreach email to a recruiter.

CANDIDATE PROFILE:
{resume_text[:2000]}

JOB DETAILS:
- Role: {role}
- Company: {company}
- Location: {location}
- Skills Required: {skills}
- Recruiter (address by this name): {recruiter}

STRICT RULES:
1. Start with: Dear {recruiter},
2. Max 160 words — be concise and punchy.
3. Mention ONE specific project from the resume that matches the required skills.
4. Highlight 2-3 matching skills naturally in one sentence.
5. Show genuine interest in {company} specifically — don't be generic.
6. Confident, professional tone — no filler phrases like "I hope this finds you well".
7. Plain text only — no markdown, no asterisks, no bullet points.
8. End with this EXACT sign-off block (copy exactly):

Warm regards,
{SENDER_NAME}
📧 {SENDER_EMAIL}
📱 {SENDER_PHONE}
🔗 LinkedIn: {SENDER_LINKEDIN}
💻 GitHub: {SENDER_GITHUB}

Output the email body ONLY — no subject line, no extra commentary.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌  '{INPUT_CSV}' not found. Run parse_jobs.py first.")
        return

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌  GROQ_API_KEY not set in .env")
        return

    client = Groq(api_key=api_key)

    # Pre-load resumes
    resume_cache = {}
    for path in [RESUME_AI, RESUME_DEV]:
        if os.path.exists(path):
            resume_cache[path] = read_pdf(path)
            print(f"  📄  Loaded resume: {path}")
        else:
            print(f"  ⚠️  Resume not found: {path} — place it in the same folder")

    with open(INPUT_CSV, encoding="utf-8") as f:
        jobs = list(csv.DictReader(f))

    print(f"\n🤖  Generating emails for {len(jobs)} job(s)...\n")

    results = []
    for i, job in enumerate(jobs, 1):
        role     = job["role"]
        company  = job["company"]
        email    = job["email"]
        skills   = job["skills"]
        location = job["location"]

        resume_file = pick_resume(role)
        resume_text = resume_cache.get(resume_file, "")
        recruiter   = first_name(email)
        subject     = generate_subject(role, company)

        print(f"  [{i}/{len(jobs)}] {company} | {role} | → {email}")
        print(f"         Resume: {resume_file} | Greeting: {recruiter}")

        try:
            body = generate_email_body(
                client, resume_text, role, company, recruiter, skills, location
            )
            status = "ready"
        except Exception as e:
            print(f"         ❌ Groq error: {e}")
            body   = ""
            status = "error"

        results.append({
            "company":  company,
            "role":     role,
            "send_to":  email,
            "recruiter": recruiter,
            "subject":  subject,
            "body":     body,
            "resume":   resume_file,
            "location": location,
            "status":   status,
        })

        if i < len(jobs):
            print(f"         ⏳ Waiting {API_DELAY_SEC}s (rate limit)...")
            time.sleep(API_DELAY_SEC)

    fieldnames = ["company", "role", "send_to", "recruiter", "subject", "body",
                  "resume", "location", "status"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    ok    = sum(1 for r in results if r["status"] == "ready")
    error = len(results) - ok
    print(f"\n✅  Done! {ok} email(s) ready, {error} error(s). Saved to '{OUTPUT_CSV}'")
    print(f"    Next step: run  python send_emails.py")


if __name__ == "__main__":
    main()
