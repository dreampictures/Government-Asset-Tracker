import re
from slugify import slugify
from datetime import datetime


def resolve_category_id(category_slug):
    if not category_slug:
        return None
    from models import Category
    cat = Category.query.filter_by(slug=category_slug).first()
    return cat.id if cat else None


def is_duplicate(title, apply_link, notification_link):
    from models import Job
    from slugify import slugify as _slugify
    slug = _slugify(title)
    if slug and Job.query.filter_by(slug=slug).first():
        return True
    if apply_link and apply_link.startswith('http'):
        if Job.query.filter_by(apply_link=apply_link).first():
            return True
    if notification_link and notification_link.startswith('http'):
        if Job.query.filter_by(notification_link=notification_link).first():
            return True
    return False


def save_jobs_to_db(all_jobs, enable_pdf=False):
    from models import db, Job
    from ai_module.generator import generate_fallback_article

    added = 0
    for job_data in all_jobs:
        title = (job_data.get('title') or '').strip()
        if not title or len(title) < 5:
            continue

        apply_link = job_data.get('apply_link', '')
        notification_link = job_data.get('notification_link', '')

        if is_duplicate(title, apply_link, notification_link):
            continue

        slug = slugify(title)
        if not slug:
            continue

        start_date = job_data.get('start_date', '')
        last_date = job_data.get('last_date', '')
        application_fee = job_data.get('application_fee', '')
        age_limit = job_data.get('age_limit', '')
        selection_process = job_data.get('selection_process', '')
        eligibility = job_data.get('eligibility', '')

        if enable_pdf and notification_link and '.pdf' in notification_link.lower():
            try:
                from scrapers.pdf_extractor import extract_from_pdf_url
                pdf_data = extract_from_pdf_url(notification_link)
                if pdf_data:
                    application_fee = pdf_data.get('application_fee') or application_fee
                    age_limit = pdf_data.get('age_limit') or age_limit
                    start_date = pdf_data.get('start_date') or start_date
                    last_date = pdf_data.get('last_date') or last_date
                    selection_process = pdf_data.get('selection_process') or selection_process
                    eligibility = pdf_data.get('eligibility') or eligibility
                    if pdf_data.get('total_posts'):
                        job_data['total_posts'] = pdf_data['total_posts']
            except Exception as e:
                print(f"[PDF] Error for {notification_link}: {e}")

        category_id = resolve_category_id(job_data.get('category_slug'))

        job = Job(
            title=title,
            slug=slug,
            organization=job_data.get('organization', ''),
            apply_link=apply_link,
            notification_link=notification_link,
            start_date=start_date,
            last_date=last_date,
            total_posts=job_data.get('total_posts', ''),
            application_fee=application_fee,
            age_limit=age_limit,
            selection_process=selection_process,
            eligibility=eligibility,
            qualification=job_data.get('qualification', ''),
            state=job_data.get('state', 'All India'),
            category_id=category_id,
            job_type=job_data.get('job_type', 'latest_jobs'),
            is_scraped=True,
            is_published=True,
        )
        db.session.add(job)
        db.session.flush()

        try:
            job.description = generate_fallback_article(job)
        except Exception:
            pass

        added += 1

    if added > 0:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[Scraper] DB commit error: {e}")
            added = 0

    return added


def run_quick_scan():
    from scrapers.sarkariresult_scraper import SarkariResultScraper
    from scrapers.freejobalert_scraper import FreeJobAlertScraper

    print("[Scraper] Starting quick scan...")
    all_jobs = []
    for ScraperClass in [SarkariResultScraper, FreeJobAlertScraper]:
        try:
            all_jobs.extend(ScraperClass().scrape())
        except Exception as e:
            print(f"[Scraper] {ScraperClass.__name__} error: {e}")

    added = save_jobs_to_db(all_jobs, enable_pdf=False)
    print(f"[Scraper] Quick scan done: {added} new jobs added from {len(all_jobs)} found")
    return added


def run_deep_scan():
    from scrapers.sarkariresult_scraper import SarkariResultScraper
    from scrapers.freejobalert_scraper import FreeJobAlertScraper
    from scrapers.ssc_scraper import SSCScraper
    from scrapers.upsc_scraper import UPSCScraper
    from scrapers.railway_scraper import RailwayScraper
    from scrapers.ibps_scraper import IBPSScraper

    print("[Scraper] Starting deep scan...")
    all_jobs = []
    for ScraperClass in [SarkariResultScraper, FreeJobAlertScraper, SSCScraper, UPSCScraper, RailwayScraper, IBPSScraper]:
        try:
            all_jobs.extend(ScraperClass().scrape())
        except Exception as e:
            print(f"[Scraper] {ScraperClass.__name__} error: {e}")

    added = save_jobs_to_db(all_jobs, enable_pdf=True)
    print(f"[Scraper] Deep scan done: {added} new jobs added from {len(all_jobs)} found")
    return added


def run_all_scrapers():
    return run_deep_scan()
