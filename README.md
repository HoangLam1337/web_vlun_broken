# Broken Access Control Lab

An intentionally vulnerable Flask + PostgreSQL web application built to study and demonstrate Broken Access Control issues in a student management system.

This project focuses on realistic authorization failures that commonly appear in API-driven web applications:

- Insecure Direct Object Reference (IDOR)
- Privilege escalation through mass assignment / unsafe profile update
- Broken function-level authorization in teacher/admin APIs
- Stored DOM XSS caused by rendering trusted API data with `innerHTML`

> This repository is for educational and portfolio purposes only. Do not deploy this application as-is.

## Project Context

The application models a simple university student management system:

- Students can view their own profile and grades.
- Teachers can view and update grades for students in their courses.
- Admins can manage accounts and view API documentation.

The vulnerable version intentionally contains authorization and frontend rendering flaws so they can be analyzed, exploited in a controlled lab, and remediated.

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Database driver | psycopg2 |
| Frontend | HTML, CSS, vanilla JavaScript |
| Runtime | Docker, Docker Compose |
| Auth state | Flask signed session cookie |

## Repository Structure

```text
.
|-- Web/
|   |-- app.py
|   |-- database.sql
|   |-- requirements.txt
|   `-- app/
|       |-- routes/
|       |-- models/
|       |-- views/
|       `-- static/
|-- Exploit/
|   `-- exploit.md
|-- docs/
|   |-- SECURITY_REPORT.md
|   |-- EXPLOIT_CHAIN.md
|   `-- REMEDIATION.md
|-- Dockerfile
|-- docker-compose.yml
`-- README.md
```

## Demo Accounts

Seed data in `Web/database.sql` creates the following lab users.

| Username | Password | Initial Role |
|---|---|---|
| `admin` | `123456` | admin |
| `GV001` | `123456` | teacher |
| `GV002` | `123456` | teacher |
| `SV001` | `123456` | student |
| `SV002` | `123456` | student |
| `SV003` | `123456` | student |
| `SV004` | `123456` | student |

## Run Locally

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:5000
```

Stop:

```bash
docker compose down
```

Reset database volume:

```bash
docker compose down -v
docker compose up --build
```

## Key Findings

| ID | Finding | Severity | OWASP Mapping |
|---|---|---:|---|
| BAC-01 | Student can read another student's grades via IDOR | High | OWASP A01, API1 BOLA |
| BAC-02 | Student can modify own role through profile API | Critical | OWASP A01, API3 BOPLA, API5 BFLA |
| BAC-03 | Teacher APIs trust role only and do not verify course ownership | High | OWASP A01, API1/API5 |
| XSS-01 | Stored DOM XSS through profile fields rendered with `innerHTML` | High | OWASP A03 Injection |

## Documentation

- [📄 Báo cáo Bảo mật (Tiếng Việt)](docs/BAO_CAO_BAO_MAT.md) ← **Báo cáo chi tiết bằng Tiếng Việt**
- [Security Report (English)](docs/SECURITY_REPORT.md)
- [Exploit Chain](docs/EXPLOIT_CHAIN.md)
- [Remediation Guide](docs/REMEDIATION.md)
- [Raw Exploit Notes](Exploit/exploit.md)

## Portfolio Summary

This project demonstrates the ability to:

- Review Flask route-level authorization logic.
- Identify object-level and function-level authorization flaws.
- Build a controlled exploit chain from a low-privilege user account.
- Explain why `HttpOnly` prevents direct cookie theft but does not stop XSS from performing authenticated actions.
- Document findings using OWASP Top 10 and OWASP API Security Top 10 terminology.
- Propose practical remediations at controller, model, session, and frontend layers.

## Safety Notes

- All exploit examples are designed for this local lab.
- The XSS webhook proof uses status-only callbacks instead of exfiltrating sensitive JSON or session cookies.
- The current source does not expose a confirmed file upload, file-write, or RCE path; the report does not claim one.
