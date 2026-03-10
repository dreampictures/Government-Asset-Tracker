# IndiaJobPortal - Government Job Portal

## Overview
A fully automated All India Government Job Portal similar to Sarkari Result / FreeJobAlert. Built with Flask, PostgreSQL, and includes web scraping, AI content generation, Telegram alerts, and email subscriptions.

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript (no framework, vanilla)
- **Database**: PostgreSQL (Replit built-in)
- **AI**: OpenAI via Replit AI Integrations (gpt-5-nano for content generation)

## Project Structure
```
app.py                  - Main Flask application with factory pattern
config.py               - Configuration (secrets, DB, SMTP)
models.py               - SQLAlchemy models (Job, Category, User, Subscriber, Notification)
routes/
  main.py               - Public routes (home, job detail, category, state, qualification, search, sitemap, robots.txt)
  admin.py              - Admin panel routes (CRUD for jobs, categories, subscribers)
  api.py                - API routes (search API, subscribe API, email alerts)
scraper/
  scraper.py            - Web scraper (SarkariResult, FreeJobAlert, EmploymentNews)
ai_module/
  generator.py          - AI content generator using OpenAI
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
- **Job Detail Pages**: SEO-optimized with structured data, breadcrumbs, view counter
- **Categories**: Central Govt, State Govt, Bank, Railway, Police, Defence, Teaching, Engineering, Medical
- **State-wise Pages**: `/state/<state-slug>` for each Indian state
- **Qualification Pages**: `/qualification/<qual-slug>` for 10th Pass, 12th Pass, Graduation, ITI, Diploma, etc.
- **Search & Filters**: By keyword, state, qualification, category, organization
- **Admin Panel**: Add/edit/delete jobs, manage categories & subscribers, run scraper, generate AI content
- **Web Scraper**: Auto-scrapes from government job sites daily (APScheduler)
- **AI Content Generator**: Converts job data to SEO articles using OpenAI
- **Telegram Bot**: Sends job alerts to configured channel
- **Email Subscription**: SMTP-based email alerts for new jobs
- **SEO**: sitemap.xml, robots.txt, meta tags, schema.org structured data, SEO-friendly URLs
- **View Counter**: Tracks job page views, powers Trending & Popular sections

## Admin Credentials
- Username: `admin`
- Password: `admin123`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit)
- `SESSION_SECRET` - Flask session secret
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (optional)
- `TELEGRAM_CHANNEL_ID` - Telegram channel ID (optional)
- `SMTP_SERVER` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM_EMAIL` - Email config (optional)
- `AI_INTEGRATIONS_OPENAI_API_KEY` / `AI_INTEGRATIONS_OPENAI_BASE_URL` - Auto-set by Replit AI integration

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
