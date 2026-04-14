# 📬 WhatsApp Job Application Automation

> **Automated cold email pipeline** — parses job leads from WhatsApp groups, generates personalized AI cold emails, and sends them with the right resume attached. **21 applications in under 5 minutes.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-F55036?style=flat)
![Gmail](https://img.shields.io/badge/Gmail-SMTP-EA4335?style=flat&logo=gmail&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live%20%26%20Working-brightgreen?style=flat)
![Applications](https://img.shields.io/badge/Emails%20Sent-21%20in%205%20mins-blue?style=flat)

---

## 🚀 What It Does

Most job portals don't allow bulk personalized outreach. WhatsApp job groups share hundreds of openings daily — but manually emailing each recruiter is slow and inconsistent.

This tool solves that in 3 steps:

1. **Paste** WhatsApp job messages into a text file
2. **Parser** extracts company, role, recruiter email, skills, location automatically
3. **AI (Groq + LLaMA 3.1)** generates a unique, personalized cold email per job
4. **Sender** attaches the right resume and fires all emails via Gmail SMTP

**Result:** 21 personalized applications with resume attachments sent in under 5 minutes.

---

## 🎥 Demo

```
$ python parse_jobs.py
📋  Parsing 'raw_jobs.txt' ...
  ✅  AB Rides Technologies    | Full-Stack Web Developer Intern  | founder@abrides.com
  ✅  Aiviio                   | AI/ML Intern (PPO)               | pramodreddy@aiviio.com
  ✅  Aarixa Innovix           | Backend Developer                | shivani@aarixainnovix.com
  ⏭️   Duplicate skipped: amritha@qpactsolutions.com
  ...
✅  Saved 21 unique job(s) to 'jobs.csv'

$ python generate_emails.py
🤖  Generating emails for 21 job(s)...
  [1/21] AB Rides Technologies | Full-Stack Web Developer Intern
         Resume: Dev_resume.pdf | Greeting: Founder
  [8/21] Aiviio | AI/ML Intern (PPO)
         Resume: AI_resume.pdf | Greeting: Pramod
  ...
✅  Done! 21 email(s) ready, 0 error(s).

$ python send_emails.py
── PREVIEW ──────────────────────────────────────────────────
  1. To: founder@abrides.com  |  AB Rides Technologies – Full-Stack Web Developer Intern
  2. To: pramodreddy@aiviio.com  |  Aiviio – AI/ML Intern (PPO)
  ...
Send all? (yes/no): yes
🚀  Connecting to Gmail SMTP...
  ✅  Logged in to Gmail
  [1/21] → founder@abrides.com   ✅  Sent
  [2/21] → hr@neogencode.com     ✅  Sent
  ...
  ✅  Sent: 21   ❌  Failed: 0
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.10+ | Core pipeline |
| AI | Groq API — LLaMA 3.1 8B Instant | Personalized email generation |
| Email | smtplib + Gmail SMTP | Sending with PDF attachments |
| PDF | pypdf | Resume text extraction for AI context |
| Parsing | Regex + emoji anchors | WhatsApp message parsing |
| Config | python-dotenv | Secure credential management |
| Storage | CSV module | Intermediate data pipeline |

---

## 📁 Project Structure

```
Whatsapp-Automation/
├── parse_jobs.py           # Step 1 — Parse WhatsApp messages → jobs.csv
├── generate_emails.py      # Step 2 — AI email generation → generated_emails.csv
├── send_emails.py          # Step 3 — Gmail SMTP sender with resume attachment
├── raw_jobs.txt            # Input  — paste WhatsApp job posts here
├── jobs.csv                # Output — parsed job data
├── generated_emails.csv    # Output — review emails before sending
├── send_log.txt            # Output — full delivery log with timestamps
├── .env.example            # Environment variable template
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Gmail account with 2-Step Verification enabled
- Free [Groq API key](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Whatsapp-Automation.git
cd Whatsapp-Automation
```

### 2. Install dependencies
```bash
pip install groq pypdf python-dotenv
```

### 3. Configure environment
```bash
cp .env.example .env
# Open .env and fill in your credentials
```

### 4. Add your resumes
Place your resume PDFs in the project folder and update the filenames in `generate_emails.py`:
```python
RESUME_AI  = "Your_AI_Resume.pdf"    # AI / ML / Prompt Engineer roles
RESUME_DEV = "Your_Dev_Resume.pdf"   # Java / Web / Full Stack roles
```

### 5. Gmail App Password
> Regular Gmail password will NOT work — Gmail blocks script logins.

`Google Account → Security → 2-Step Verification → App Passwords → Generate`

Use the 16-character password as `EMAIL_PASS` in your `.env`.

---

## 🔄 Daily Workflow

```bash
# 1. Paste fresh WhatsApp job messages into raw_jobs.txt (clear old ones first)

# 2. Parse jobs
python parse_jobs.py

# 3. Generate personalized emails
python generate_emails.py

# 4. Review generated_emails.csv — edit any email body if needed

# 5. Send
python send_emails.py
```

---

## 🧠 How AI Email Generation Works

Each email is generated with this context sent to LLaMA 3.1 8B:

| Input | Source |
|-------|--------|
| Your resume text | Extracted live from PDF via pypdf |
| Job role & company | Parsed from WhatsApp message |
| Required skills | Parsed from WhatsApp message |
| Recruiter first name | Extracted from email address (e.g. `shivani@` → "Shivani") |

**Prompt constraints enforced:**
- Max 160 words — punchy, not padded
- Must mention ONE specific project matching the role's skills
- Address recruiter by first name
- No generic filler phrases
- Plain text only, consistent sign-off with contact links

---

## 🔀 Smart Resume Selection

```python
AI_KEYWORDS = ["ai", "ml", "llm", "prompt", "nlp", "generative", "deep learning", ...]

def pick_resume(role):
    if any(kw in role.lower() for kw in AI_KEYWORDS):
        return RESUME_AI   # AI/ML roles
    return RESUME_DEV      # All other dev roles
```

Simple keyword match — no ML needed for this decision.

---

## 🛡️ Built-in Safeguards

| Safeguard | How |
|-----------|-----|
| Duplicate prevention | Same email in multiple posts → sent only once |
| Preview before send | Full list shown, requires "yes" confirmation |
| Groq rate limiting | 6s delay between API calls (free tier safe) |
| Gmail rate limiting | 3s delay between sends |
| Delivery log | Every result saved to `send_log.txt` |
| Resume validation | Warns if PDF not found before generating |

---

## 📊 Live Results

| Metric | Result |
|--------|--------|
| WhatsApp posts processed | 23 |
| Duplicate emails removed | 2 |
| Unique applications sent | 21 |
| Failed sends | 0 |
| Total pipeline time | ~5 minutes |

---

## 🔮 Planned Improvements

- [ ] WhatsApp Web automation — auto-read messages without manual paste
- [ ] Streamlit UI for non-technical users
- [ ] Email open/reply tracking
- [ ] Google Sheets dashboard for application status
- [ ] Auto follow-up email after 3 days with no reply

---

## ⚠️ Disclaimer

Built for personal job applications only. Always review AI-generated emails before sending. Use responsibly and respect recruiter preferences.

---

## 👨‍💻 Author

**Tejendra Ayyappa Reddy Syamala**  
B.E. Computer Science Engineering (Data Science) — Sathyabama University  
Ex Prompt Engineer & AI Engineer Intern @ Cortexus.AI

[![LinkedIn](https://www.linkedin.com/in/tejendra-ayyappa-reddy/)
[![GitHub](https://github.com/Tejendra-dev)

---

## 📄 License

MIT License — free to use, modify, and build on.
