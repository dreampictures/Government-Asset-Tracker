# IndiaJobPortal - Government Job Portal

## Overview
A fully automated All India Government Job Portal similar to Sarkari Result / FreeJobAlert. Built with Flask, PostgreSQL, and includes modular web scraping, PDF extraction, AI content generation (Ollama/Llama3), Telegram alerts, and email subscriptions (Resend).

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript (no framework, vanilla)
- **Database**: PostgreSQL (Replit built-in / Neon free tier for deployment)
- **AI**: Ollama with Llama3 open-source model (free, self-hosted) + template fallback
- **Email**: Resend free tier (REST API)
- **Telegram**: Telegram Bot API (free)
- **PDF Extraction**: pdfminer.six + PyPDF2
- **Scheduler**: APScheduler (quick scan every 3h, deep scan daily at 2 AM)

## Project Structure
```
app.py                  - Main Flask application with factory pattern
config.py               - Configuration (secrets, DB, Ollama, Resend, WhatsApp)
models.py               - SQLAlchemy models (Job, Category, User, Subscriber, Notification)
extensions.py           - Flask extensions (db, login_manager, csrf, cache)
routes/
  main.py               - Public routes (home, job detail, category, state, qualification, search)
  admin.py              - Admin panel routes (CRUD, scraped jobs review, bulk approve)
  api.py                - API routes (search, subscribe, email alerts)
scraper/
  scraper.py            - Wrapper entry point (calls new modular scrapers/)
scrapers/               - Modular scraper system
  __init__.py           - Main entry: run_quick_scan(), run_deep_scan(), run_all_scrapers()
  base_scraper.py       - Base class with common utilities (detect category/state/type/qualification)
  sarkariresult_scraper.py - SarkariResult.com scraper (latest, admit, result, answer key)
  freejobalert_scraper.py  - FreeJobAlert.com scraper (notifications, admit, results)
  ssc_scraper.py        - SSC official website scraper
  upsc_scraper.py       - UPSC official website scraper
  railway_scraper.py    - Railway (RRB/RRC) scraper
  ibps_scraper.py       - IBPS banking recruitment scraper
  pdf_extractor.py      - PDF download and text extraction (pdfminer.six / PyPDF2)
ai_module/
  generator.py          - AI content generator (Ollama/Llama3 + template fallback)
telegram_bot/
  bot.py                - Telegram bot for job alerts
templates/              - Jinja2 templates (base, index, job_detail, category, state, qualification, search)
  admin/                - Admin panel templates including scraped_jobs.html
static/
  css/style.css         - Main stylesheet
  js/main.js            - JavaScript
  uploads/              - Uploaded notification PDFs
```

## Features
- **Auto Scraping**: 6 modular scrapers (SarkariResult, FreeJobAlert, SSC, UPSC, Railway, IBPS)
- **Auto Scheduling**: Quick scan every 3 hours, deep scan daily at 2 AM with PDF extraction
- **PDF Extraction**: Automatically downloads and parses notification PDFs for structured data
- **Auto Job Type Detection**: Classifies as Latest Jobs, Admit Card, Result, Answer Key, Syllabus, Admission
- **Duplicate Detection**: Checks slug + apply_link + notification_link before creating
- **AI Content**: Auto-generates structured job articles using Ollama/Llama3 or template fallback
- **Scraped Jobs Review**: Admin can approve/reject/bulk-approve scraped jobs
- **Hidden Admin**: Admin accessible only via /admin-login (masked username input)
- **Categories**: Central Govt, State Govt, Bank, Railway, Police, Defence, Teaching, Engineering, Medical
- **State-wise / Qualification pages** with live job counts
- **Search & Filters**: By keyword, state, qualification, category, organization
- **SEO**: sitemap.xml, robots.txt, meta tags, schema.org structured data
- **Telegram Bot**: Job alerts to configured channel
- **Email Subscriptions**: Resend free tier
- **View Counter**: Tracks job page views for trending/popular sections
- **CSRF Protection**: All forms protected

## Admin Access
- **URL**: `/admin-login` (hidden, not linked anywhere on the public site)
- **Username**: `714752420017` (masked input)
- **Password**: `Ba@606368`

## Scheduler
- Quick scan: Every 3 hours — SarkariResult + FreeJobAlert (fast, no PDF)
- Deep scan: Daily at 2 AM — All 6 sources + PDF extraction

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session secret
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (optional)
- `TELEGRAM_CHANNEL_ID` - Telegram channel ID (optional)
- `RESEND_API_KEY` - Resend API key for email alerts (optional)
- `RESEND_FROM_EMAIL` - Sender email (default: onboarding@resend.dev)
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Ollama model name (default: llama3)
- `WHATSAPP_CHANNEL_URL` - WhatsApp channel URL (optional)

## Key URLs
- `/` - Homepage
- `/job/<slug>` - Job detail page
- `/category/<slug>` - Category page
- `/state/<slug>` - State-wise jobs
- `/qualification/<slug>` - Qualification-wise jobs
- `/latest-notifications` - All notifications
- `/search` - Advanced search
- `/jobs/<type>` - Jobs by type
- `/admin-login` - Hidden admin entry point
- `/admin/` - Admin dashboard (requires login)
- `/admin/scraped-jobs` - Review scraped jobs
- `/sitemap.xml` - SEO sitemap
- `/robots.txt` - Robots file
