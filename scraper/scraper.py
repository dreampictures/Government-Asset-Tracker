import re
import random
import requests
from bs4 import BeautifulSoup
from slugify import slugify
from datetime import datetime

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

REQUEST_TIMEOUT = 20

DATE_PATTERNS = [
    re.compile(r'(\d{2}[-/]\d{2}[-/]\d{4})'),
    re.compile(r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', re.IGNORECASE),
    re.compile(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', re.IGNORECASE),
]

POST_COUNT_PATTERN = re.compile(r'(\d{2,6})\s*(?:posts?|vacancies|vacancy|openings?|seats?)', re.IGNORECASE)
POST_COUNT_PATTERN_ALT = re.compile(r'(?:recruit|hiring)\s*(\d{2,6})', re.IGNORECASE)
TITLE_POST_PATTERN = re.compile(r'(?:^|\s)(\d{2,6})\s+(?:group|grade|asst|assistant|clerk|constable|si\b|sub\s*inspector)', re.IGNORECASE)

CATEGORY_KEYWORDS = {
    'bank-jobs': ['bank', 'ibps', 'sbi', 'rbi', 'nabard', 'idbi', 'banking'],
    'railway-jobs': ['railway', 'rrb', 'rrc', 'indian railways', 'rail'],
    'central-govt-jobs': ['ssc', 'staff selection', 'upsc', 'union public service', 'ias', 'ips', 'civil services', 'central govt', 'central government', 'ministry', 'department of', 'court', 'judicial', 'high court', 'supreme court', 'district court'],
    'defence-jobs': ['army', 'navy', 'air force', 'defence', 'defense', 'military', 'bsf', 'crpf', 'cisf', 'itbp', 'ssb', 'nda', 'cds', 'territorial'],
    'police-jobs': ['police', 'constable', 'sub inspector', 'si ', 'ssc gd', 'inspector'],
    'teaching-jobs': ['teacher', 'teaching', 'tgt', 'pgt', 'ctet', 'tet', 'lecturer', 'professor', 'faculty', 'education'],
    'engineering-jobs': ['engineer', 'engineering', 'technical', 'je ', 'junior engineer', 'ae ', 'assistant engineer'],
    'medical-jobs': ['doctor', 'medical', 'nurse', 'nursing', 'health', 'hospital', 'pharmacist', 'aiims', 'mbbs', 'anm', 'gnm', 'staff nurse'],
    'state-govt-jobs': ['state govt', 'state government', 'psc', 'ppsc', 'bpsc', 'uppsc', 'mpsc', 'rpsc', 'gpsc', 'appsc', 'tspsc', 'kpsc', 'wbpsc', 'opsc', 'hpsc', 'jpsc'],
}

STATE_KEYWORDS = {
    'Andhra Pradesh': ['andhra pradesh', 'appsc', 'ap govt', 'ap police'],
    'Bihar': ['bihar', 'bpsc', 'bssc', 'bihar police'],
    'Chhattisgarh': ['chhattisgarh', 'cgpsc'],
    'Delhi': ['delhi', 'dsssb'],
    'Gujarat': ['gujarat', 'gpsc', 'gsssb'],
    'Haryana': ['haryana', 'hssc', 'hpsc'],
    'Himachal Pradesh': ['himachal pradesh', 'hppsc'],
    'Jharkhand': ['jharkhand', 'jpsc', 'jssc'],
    'Karnataka': ['karnataka', 'kpsc', 'kea'],
    'Kerala': ['kerala', 'kpsc kerala', 'kerala psc'],
    'Madhya Pradesh': ['madhya pradesh', 'mppsc', 'mp govt', 'mp police'],
    'Maharashtra': ['maharashtra', 'mpsc', 'maharashtra psc'],
    'Odisha': ['odisha', 'opsc', 'osssc'],
    'Punjab': ['punjab', 'ppsc', 'punjab psc'],
    'Rajasthan': ['rajasthan', 'rpsc', 'rsmssb'],
    'Tamil Nadu': ['tamil nadu', 'tnpsc', 'mrb'],
    'Telangana': ['telangana', 'tspsc'],
    'Uttar Pradesh': ['uttar pradesh', 'uppsc', 'upsssc', 'up police'],
    'Uttarakhand': ['uttarakhand', 'ukpsc', 'uksssc'],
    'West Bengal': ['west bengal', 'wbpsc', 'wbssc'],
    'Jammu and Kashmir': ['jammu', 'kashmir', 'jkpsc', 'jkssb'],
    'Assam': ['assam', 'apsc assam'],
    'Goa': ['goa'],
    'Manipur': ['manipur'],
    'Meghalaya': ['meghalaya'],
    'Mizoram': ['mizoram'],
    'Nagaland': ['nagaland'],
    'Sikkim': ['sikkim'],
    'Tripura': ['tripura'],
    'Arunachal Pradesh': ['arunachal pradesh'],
}

QUALIFICATION_KEYWORDS = {
    '10th Pass': ['10th pass', '10th', 'matriculation', 'sslc', 'class 10', 'class x'],
    '12th Pass': ['12th pass', '12th', 'intermediate', 'higher secondary', 'class 12', 'class xii', 'hsc'],
    'Graduation': ['graduation', 'graduate', 'degree', 'bachelor', 'b.a', 'b.sc', 'b.com'],
    'Post Graduation': ['post graduation', 'post graduate', 'master', 'm.a', 'm.sc', 'm.com', 'mba'],
    'B.Tech/B.E.': ['b.tech', 'b.e.', 'engineering degree', 'btech'],
    'ITI': ['iti'],
    'Diploma': ['diploma'],
    'MBBS': ['mbbs'],
    'LLB': ['llb', 'law degree'],
    'B.Ed': ['b.ed', 'bed'],
}


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }


def safe_request(url, timeout=REQUEST_TIMEOUT):
    try:
        response = requests.get(url, headers=get_headers(), timeout=timeout)
        if response.status_code == 200:
            return response
    except requests.exceptions.Timeout:
        print(f"Request timeout for {url}")
    except requests.exceptions.ConnectionError:
        print(f"Connection error for {url}")
    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
    return None


def extract_date(text):
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return ''


def extract_post_count(text):
    match = POST_COUNT_PATTERN.search(text)
    if match:
        return match.group(1)
    match = TITLE_POST_PATTERN.search(text)
    if match:
        return match.group(1)
    match = POST_COUNT_PATTERN_ALT.search(text)
    if match:
        return match.group(1)
    return ''


def detect_category(title):
    title_lower = title.lower()
    for slug, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return slug
    return None


def detect_state(title):
    title_lower = title.lower()
    for state, keywords in STATE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return state
    return 'All India'


def detect_qualification(title):
    title_lower = title.lower()
    for qual, keywords in QUALIFICATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return qual
    return ''


def enrich_job_data(job_data):
    title = job_data.get('title', '')
    if not job_data.get('last_date'):
        job_data['last_date'] = extract_date(title)
    if not job_data.get('total_posts'):
        job_data['total_posts'] = extract_post_count(title)
    if not job_data.get('category_slug'):
        job_data['category_slug'] = detect_category(title)
    if not job_data.get('state') or job_data['state'] == 'All India':
        job_data['state'] = detect_state(title)
    if not job_data.get('qualification'):
        job_data['qualification'] = detect_qualification(title)
    return job_data


def extract_org_from_title(title):
    parts = title.split('-')
    if len(parts) > 1:
        return parts[0].strip()
    parts = title.split(':')
    if len(parts) > 1:
        return parts[0].strip()
    words = title.split()
    return ' '.join(words[:3]) if len(words) > 3 else title


def scrape_sarkari_result():
    jobs = []
    try:
        url = 'https://www.sarkariresult.com/latestjob.php'
        response = safe_request(url)
        if not response:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        job_links = soup.select('td a[href]')

        for link in job_links[:30]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and href and len(title) > 10:
                job = {
                    'title': title,
                    'organization': extract_org_from_title(title),
                    'apply_link': href if href.startswith('http') else f'https://www.sarkariresult.com/{href}',
                    'notification_link': '',
                    'last_date': '',
                    'total_posts': '',
                    'qualification': '',
                    'state': 'All India',
                    'category_slug': None,
                    'source': 'sarkariresult',
                }
                jobs.append(enrich_job_data(job))
    except Exception as e:
        print(f"Scraper error (sarkariresult): {e}")
    return jobs


def scrape_free_job_alert():
    jobs = []
    try:
        url = 'https://www.freejobalert.com/latest-notifications/page/1/'
        response = safe_request(url)
        if not response:
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
                        job = {
                            'title': title,
                            'organization': extract_org_from_title(title),
                            'apply_link': href,
                            'notification_link': '',
                            'last_date': last_date,
                            'total_posts': '',
                            'qualification': '',
                            'state': 'All India',
                            'category_slug': None,
                            'source': 'freejobalert',
                        }
                        jobs.append(enrich_job_data(job))
    except Exception as e:
        print(f"Scraper error (freejobalert): {e}")
    return jobs


def scrape_employment_news():
    jobs = []
    try:
        url = 'https://www.employmentnews.gov.in/NewEmp/Aborad.aspx'
        response = safe_request(url)
        if not response:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('a[href]')

        for link in links[:20]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if title and len(title) > 15 and ('recruitment' in title.lower() or 'vacancy' in title.lower() or 'notification' in title.lower()):
                job = {
                    'title': title,
                    'organization': extract_org_from_title(title),
                    'apply_link': href if href.startswith('http') else f'https://www.employmentnews.gov.in/{href}',
                    'notification_link': '',
                    'last_date': '',
                    'total_posts': '',
                    'qualification': '',
                    'state': 'All India',
                    'category_slug': None,
                    'source': 'employmentnews',
                }
                jobs.append(enrich_job_data(job))
    except Exception as e:
        print(f"Scraper error (employmentnews): {e}")
    return jobs


def scrape_ncs_portal():
    jobs = []
    try:
        url = 'https://www.ncs.gov.in/content-repository/Pages/Government-Jobs.aspx'
        response = safe_request(url)
        if not response:
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table tr')

        for row in rows[:30]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                link = cells[0].find('a') or row.find('a')
                if link:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    if title and len(title) > 10:
                        last_date = ''
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            extracted = extract_date(cell_text)
                            if extracted:
                                last_date = extracted
                                break

                        job = {
                            'title': title,
                            'organization': extract_org_from_title(title),
                            'apply_link': href if href.startswith('http') else f'https://www.ncs.gov.in{href}',
                            'notification_link': '',
                            'last_date': last_date,
                            'total_posts': '',
                            'qualification': '',
                            'state': 'All India',
                            'category_slug': None,
                            'source': 'ncs',
                        }
                        jobs.append(enrich_job_data(job))

        if not jobs:
            all_links = soup.select('a[href]')
            for link in all_links[:25]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                if title and len(title) > 15 and any(kw in title.lower() for kw in ['recruitment', 'vacancy', 'notification', 'posts', 'jobs']):
                    job = {
                        'title': title,
                        'organization': extract_org_from_title(title),
                        'apply_link': href if href.startswith('http') else f'https://www.ncs.gov.in{href}',
                        'notification_link': '',
                        'last_date': extract_date(title),
                        'total_posts': '',
                        'qualification': '',
                        'state': 'All India',
                        'category_slug': None,
                        'source': 'ncs',
                    }
                    jobs.append(enrich_job_data(job))
    except Exception as e:
        print(f"Scraper error (ncs): {e}")
    return jobs


def resolve_category_id(category_slug):
    if not category_slug:
        return None
    from models import Category
    category = Category.query.filter_by(slug=category_slug).first()
    if category:
        return category.id
    return None


def run_scraper():
    from models import db, Job
    from flask import current_app

    all_jobs = []
    all_jobs.extend(scrape_sarkari_result())
    all_jobs.extend(scrape_free_job_alert())
    all_jobs.extend(scrape_employment_news())
    all_jobs.extend(scrape_ncs_portal())

    added = 0
    for job_data in all_jobs:
        slug = slugify(job_data['title'])
        if not slug:
            continue

        existing = Job.query.filter_by(slug=slug).first()
        if existing:
            continue

        category_id = resolve_category_id(job_data.get('category_slug'))

        job = Job(
            title=job_data['title'],
            slug=slug,
            organization=job_data.get('organization', ''),
            apply_link=job_data.get('apply_link', ''),
            notification_link=job_data.get('notification_link', ''),
            last_date=job_data.get('last_date', ''),
            total_posts=job_data.get('total_posts', ''),
            qualification=job_data.get('qualification', ''),
            state=job_data.get('state', 'All India'),
            category_id=category_id,
            is_scraped=True,
            is_published=True,
            job_type='latest_jobs',
        )
        db.session.add(job)
        added += 1

    if added > 0:
        db.session.commit()

    print(f"Scraper completed: {added} new jobs added out of {len(all_jobs)} found")
    return added
