import requests
from bs4 import BeautifulSoup
from slugify import slugify
from datetime import datetime


def scrape_sarkari_result():
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = 'https://www.sarkariresult.com/latestjob.php'
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        job_links = soup.select('td a[href]')

        for link in job_links[:30]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and href and len(title) > 10:
                jobs.append({
                    'title': title,
                    'organization': extract_org_from_title(title),
                    'apply_link': href if href.startswith('http') else f'https://www.sarkariresult.com/{href}',
                    'notification_link': '',
                    'last_date': '',
                    'source': 'sarkariresult'
                })
    except Exception as e:
        print(f"Scraper error (sarkariresult): {e}")
    return jobs


def scrape_free_job_alert():
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = 'https://www.freejobalert.com/latest-notifications/page/1/'
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table.border_bottom_none tr')

        for row in rows[:30]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                link = cells[0].find('a')
                if link:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    last_date = cells[-1].get_text(strip=True) if len(cells) > 1 else ''
                    if title and len(title) > 10:
                        jobs.append({
                            'title': title,
                            'organization': extract_org_from_title(title),
                            'apply_link': href,
                            'notification_link': '',
                            'last_date': last_date,
                            'source': 'freejobalert'
                        })
    except Exception as e:
        print(f"Scraper error (freejobalert): {e}")
    return jobs


def scrape_employment_news():
    jobs = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = 'https://www.employmentnews.gov.in/NewEmp/Aborad.aspx'
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('a[href]')

        for link in links[:20]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and len(title) > 15 and ('recruitment' in title.lower() or 'vacancy' in title.lower() or 'notification' in title.lower()):
                jobs.append({
                    'title': title,
                    'organization': extract_org_from_title(title),
                    'apply_link': href if href.startswith('http') else f'https://www.employmentnews.gov.in/{href}',
                    'notification_link': '',
                    'last_date': '',
                    'source': 'employmentnews'
                })
    except Exception as e:
        print(f"Scraper error (employmentnews): {e}")
    return jobs


def extract_org_from_title(title):
    parts = title.split('-')
    if len(parts) > 1:
        return parts[0].strip()
    parts = title.split(':')
    if len(parts) > 1:
        return parts[0].strip()
    words = title.split()
    return ' '.join(words[:3]) if len(words) > 3 else title


def run_scraper():
    from models import db, Job
    from flask import current_app

    all_jobs = []
    all_jobs.extend(scrape_sarkari_result())
    all_jobs.extend(scrape_free_job_alert())
    all_jobs.extend(scrape_employment_news())

    added = 0
    for job_data in all_jobs:
        slug = slugify(job_data['title'])
        if not slug:
            continue

        existing = Job.query.filter_by(slug=slug).first()
        if existing:
            continue

        job = Job(
            title=job_data['title'],
            slug=slug,
            organization=job_data.get('organization', ''),
            apply_link=job_data.get('apply_link', ''),
            notification_link=job_data.get('notification_link', ''),
            last_date=job_data.get('last_date', ''),
            is_scraped=True,
            is_published=True,
            job_type='latest_jobs'
        )
        db.session.add(job)
        added += 1

    if added > 0:
        db.session.commit()

    print(f"Scraper completed: {added} new jobs added out of {len(all_jobs)} found")
    return added
