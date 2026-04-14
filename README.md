# Beebom SEO Testing Framework

Automated SEO testing framework for [beebom.com](https://beebom.com) built with Python, Playwright, and pytest.

## Features

- **Meta tag validation** — title, description, OG tags, canonical, robots
- **Heading structure** — H1 uniqueness, hierarchy, keyword presence
- **Link checks** — broken links, redirect chains, nofollow audit
- **Performance** — page load time, TTFB, image sizes, request count
- **Mobile responsiveness** — viewport, tap targets, font sizes, layout
- **Structured data** — JSON-LD validation, Article/Organization/Breadcrumb schemas
- **Security** — HTTPS enforcement, mixed content, robots.txt, sitemap, headers
- **HTML email reports** with trend analysis
- **SQLite result history** for regression tracking
- **Docker support** for containerised runs
- **GitHub Actions** nightly CI pipeline

## Quick Start

### 1. Clone and install

```bash
git clone <repo-url>
cd beebom-seo-framework
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your SMTP credentials and recipients
```

### 3. Run tests

```bash
# Full suite
pytest tests/

# Smoke tests only
pytest tests/ -m smoke

# Specific category
pytest tests/test_meta_tags.py -v

# With HTML report
pytest tests/ --html=reports/report.html
```

### 4. View Allure report

```bash
allure serve reports/allure-results
```

## Docker

```bash
# Build and run
docker-compose up --build

# Reports are mounted to ./reports/
```

## Nightly Scheduler

```bash
# Run as background process — executes at 11 PM IST daily
python scheduler.py

# Run immediately then continue scheduling
python scheduler.py --now
```

## GitHub Actions

The workflow runs automatically at 11 PM IST (5:30 PM UTC) every night.

Required GitHub Secrets:
- `BASE_URL` — target URL (default: https://beebom.com)
- `SMTP_EMAIL` — Gmail address for sending reports
- `SMTP_PASSWORD` — Gmail app password
- `REPORT_RECIPIENTS` — comma-separated email list

## Project Structure

```
beebom-seo-framework/
├── .github/workflows/     # CI/CD
├── pages/                 # Page Object Model
├── tests/                 # All test files
├── utils/                 # DB logger, email reporter, crawler
├── data/                  # URL lists
├── reports/               # Generated reports
├── Dockerfile
├── docker-compose.yml
├── scheduler.py
├── pytest.ini
└── requirements.txt
```

## Test Markers

| Marker        | Description                    |
|---------------|--------------------------------|
| `smoke`       | Critical SEO checks            |
| `regression`  | Full SEO regression suite       |
| `performance` | Page speed checks               |
| `mobile`      | Mobile responsiveness checks    |
| `security`    | Security and HTTPS checks       |

Run specific markers:

```bash
pytest -m smoke
pytest -m "not performance"
```
