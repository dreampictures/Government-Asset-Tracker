# IndiaJobPortal - Government Job Portal

## Overview
A fully automated All India Government Job Portal similar to Sarkari Result / FreeJobAlert. Built with Flask, PostgreSQL, and includes web scraping, AI content generation (Ollama/Llama3), Telegram alerts, and email subscriptions (Resend).

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript (no framework, vanilla)
- **Database**: PostgreSQL (Replit built-in / Neon free tier for deployment)
- **AI**: Ollama with Llama3 open-source model (free, self-hosted)
- **Email**: Resend free tier (REST API)
- **Telegram**: Telegram Bot API (free)
- **Hosting**: Fly.io compatible

## Project Structure
```
app.py                  - Main Flask application with factory pattern
config.py               - Configuration (secrets, DB, Ollama, Resend)
models.py               - SQLAlchemy models (Job, Category, User, Subscriber, Notification)
routes/
  main.py               - Public routes (home, job detail, category, state, qualification, search, sitemap, robots.txt)
  admin.py              - Admin panel routes (CRUD for jobs, categories, subscribers)
  api.py                - API routes (search API, subscribe API, email alerts via Resend)
scraper/
  scraper.py            - Web scraper (SarkariResult, FreeJobAlert, EmploymentNews)
ai_module/
  generator.py          - AI content generator using Ollama/Llama3 (falls back to template-based generation)
telegram_bot/
  bot.py                - Telegram bot for job alerts
templates/              - Jinja2 templates (base, index, job_detail, category, state, qualification, search, admin/*)
static/
  css/style.css         - Main stylesheet (responsive, professional UI)
  js/main.js            - JavaScript (navigation, lazy loading, flash messages)
  uploads/              - Uploaded notification PDFs
```

## Features
- **Homepage**: Latest Jobs, Trending Jobs, Popular Jobs, Admit Cards, Results, Answer Keys, Syllabus, Admissions
- **Job Detail Pages**: 10 structured sections (Introduction, Important Dates, Application Fee, Age Limit, Vacancy Details, Eligibility, Salary, Selection Process, How to Apply, Important Links) + SEO schema markup
- **Categories**: Central Govt, State Govt, Bank, Railway, Police, Defence, Teaching, Engineering, Medical
- **State-wise Pages**: `/state/<state-slug>` for each Indian state
- **Qualification Pages**: `/qualification/<qual-slug>` for 10th Pass, 12th Pass, Graduation, ITI, Diploma, etc.
- **Search & Filters**: By keyword, state, qualification, category, organization
- **Admin Panel**: Add/edit/delete jobs, manage categories, subscribers & notifications, run scraper, generate AI content
- **Caching**: Flask-Caching (SimpleCache) with 5-min TTL for homepage, 10-min TTL for category/state/qualification pages; auto-invalidated on admin changes
- **Web Scraper**: Auto-scrapes from government job sites daily (APScheduler)
- **AI Content Generator**: Uses Ollama/Llama3 (free) with template-based fallback
- **Telegram Bot**: Sends job alerts to configured channel (free)
- **Email Subscription**: Resend free tier email alerts for new jobs
- **SEO**: sitemap.xml, robots.txt, meta tags, schema.org structured data, SEO-friendly URLs
- **View Counter**: Tracks job page views, powers Trending & Popular sections
- **CSRF Protection**: All POST forms protected with Flask-WTF CSRF tokens

## Admin Credentials
- Username: `admin`
- Password: `admin123`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit, or Neon free tier URL)
- `SESSION_SECRET` - Flask session secret
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (optional, free)
- `TELEGRAM_CHANNEL_ID` - Telegram channel ID (optional, free)
- `RESEND_API_KEY` - Resend API key for email alerts (optional, free tier)
- `RESEND_FROM_EMAIL` - Sender email address for Resend (default: onboarding@resend.dev)
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Ollama model name (default: llama3)

## Key URLs
- `/` - Homepage
- `/job/<slug>` - Job detail page
- `/category/<slug>` - Category page
- `/state/<slug>` - State-wise jobs page
- `/qualification/<slug>` - Qualification-wise jobs page
- `/search` - Advanced search
- `/jobs/<type>` - Jobs by type (latest_jobs, admit_card, result, etc.)
- `/admin/` - Admin dashboard
- `/sitemap.xml` - SEO sitemap
- `/robots.txt` - Robots file

## Cost Policy
This project uses ONLY free and open-source tools:
- Database: PostgreSQL (Replit built-in or Neon free tier)
- AI: Ollama + Llama3 (free, open-source, self-hosted)
- Email: Resend free tier (100 emails/day)
- Telegram: Bot API (free)
- No paid APIs or subscriptions required
