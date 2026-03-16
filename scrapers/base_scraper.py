import re
import random
import requests

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]

DATE_PATTERNS = [
    re.compile(r'(\d{2}[-/]\d{2}[-/]\d{4})'),
    re.compile(r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', re.IGNORECASE),
    re.compile(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', re.IGNORECASE),
]

POST_COUNT_PATTERN = re.compile(r'(\d{2,6})\s*(?:posts?|vacancies|vacancy|openings?|seats?)', re.IGNORECASE)
TITLE_POST_PATTERN = re.compile(r'(?:^|\s)(\d{2,6})\s+(?:group|grade|asst|assistant|clerk|constable|si\b|sub\s*inspector)', re.IGNORECASE)
POST_COUNT_ALT = re.compile(r'(?:recruit|hiring)\s*(\d{2,6})', re.IGNORECASE)

CATEGORY_KEYWORDS = {
    'bank-jobs': ['bank', 'ibps', 'sbi', 'rbi', 'nabard', 'idbi', 'banking'],
    'railway-jobs': ['railway', 'rrb', 'rrc', 'indian railways', 'rail'],
    'central-govt-jobs': ['ssc', 'staff selection', 'upsc', 'union public service', 'ias', 'ips', 'civil services',
                          'central govt', 'central government', 'ministry', 'department of', 'court', 'judicial',
                          'high court', 'supreme court', 'district court'],
    'defence-jobs': ['army', 'navy', 'air force', 'defence', 'defense', 'military', 'bsf', 'crpf', 'cisf',
                     'itbp', 'ssb', 'nda', 'cds', 'territorial'],
    'police-jobs': ['police', 'constable', 'sub inspector', 'si ', 'ssc gd', 'inspector'],
    'teaching-jobs': ['teacher', 'teaching', 'tgt', 'pgt', 'ctet', 'tet', 'lecturer', 'professor', 'faculty', 'education'],
    'engineering-jobs': ['engineer', 'engineering', 'technical', 'je ', 'junior engineer', 'ae ', 'assistant engineer'],
    'medical-jobs': ['doctor', 'medical', 'nurse', 'nursing', 'health', 'hospital', 'pharmacist', 'aiims', 'mbbs', 'anm', 'gnm', 'staff nurse'],
    'state-govt-jobs': ['state govt', 'state government', 'psc', 'ppsc', 'bpsc', 'uppsc', 'mpsc', 'rpsc', 'gpsc',
                        'appsc', 'tspsc', 'kpsc', 'wbpsc', 'opsc', 'hpsc', 'jpsc'],
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
    'Kerala': ['kerala', 'kerala psc'],
    'Madhya Pradesh': ['madhya pradesh', 'mppsc', 'mp govt', 'mp police'],
    'Maharashtra': ['maharashtra', 'mpsc'],
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
}

QUALIFICATION_KEYWORDS = {
    '10th Pass': ['10th pass', '10th', 'matriculation', 'sslc', 'class 10', 'class x'],
    '12th Pass': ['12th pass', '12th', 'intermediate', 'higher secondary', 'class 12', 'hsc'],
    'Graduation': ['graduation', 'graduate', 'degree', 'bachelor', 'b.a', 'b.sc', 'b.com'],
    'Post Graduation': ['post graduation', 'post graduate', 'master', 'm.a', 'm.sc', 'm.com', 'mba'],
    'B.Tech/B.E.': ['b.tech', 'b.e.', 'engineering degree', 'btech'],
    'ITI': ['iti'],
    'Diploma': ['diploma'],
    'MBBS': ['mbbs'],
    'LLB': ['llb', 'law degree'],
    'B.Ed': ['b.ed', 'bed'],
}

JOB_TYPE_KEYWORDS = {
    'admit_card': ['admit card', 'hall ticket', 'call letter', 'e-admit', 'admit letter'],
    'result': ['result', 'results', 'merit list', 'final result', 'cut off', 'cutoff', 'selected candidates', 'score card', 'scorecard'],
    'answer_key': ['answer key', 'answer sheet', 'provisional answer', 'final answer key', 'objection answer'],
    'syllabus': ['syllabus', 'exam pattern', 'curriculum'],
    'admission': ['admission', 'counselling', 'counseling', 'seat allotment', 'neet', 'jee'],
}


class BaseScraper:
    REQUEST_TIMEOUT = 20

    def __init__(self, source_name):
        self.source_name = source_name

    def get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-IN,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def safe_request(self, url, timeout=None):
        timeout = timeout or self.REQUEST_TIMEOUT
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return response
            print(f"[{self.source_name}] HTTP {response.status_code} for {url}")
        except requests.exceptions.Timeout:
            print(f"[{self.source_name}] Timeout: {url}")
        except requests.exceptions.ConnectionError:
            print(f"[{self.source_name}] Connection error: {url}")
        except requests.exceptions.RequestException as e:
            print(f"[{self.source_name}] Request error: {url} — {e}")
        return None

    def extract_date(self, text):
        for pattern in DATE_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return ''

    def extract_all_dates(self, text):
        dates = []
        for pattern in DATE_PATTERNS:
            dates.extend(pattern.findall(text))
        return dates

    def extract_post_count(self, text):
        m = POST_COUNT_PATTERN.search(text)
        if m:
            return m.group(1)
        m = TITLE_POST_PATTERN.search(text)
        if m:
            return m.group(1)
        m = POST_COUNT_ALT.search(text)
        if m:
            return m.group(1)
        return ''

    def detect_category(self, title):
        title_lower = title.lower()
        for slug, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    return slug
        return None

    def detect_state(self, title):
        title_lower = title.lower()
        for state, keywords in STATE_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    return state
        return 'All India'

    def detect_qualification(self, title):
        title_lower = title.lower()
        for qual, keywords in QUALIFICATION_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    return qual
        return ''

    def detect_job_type(self, title):
        title_lower = title.lower()
        for job_type, keywords in JOB_TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in title_lower:
                    return job_type
        return 'latest_jobs'

    def extract_org_from_title(self, title):
        for sep in ['-', ':']:
            parts = title.split(sep)
            if len(parts) > 1:
                return parts[0].strip()
        words = title.split()
        return ' '.join(words[:3]) if len(words) > 3 else title

    def build_absolute_url(self, href, base_url):
        if not href:
            return ''
        if href.startswith('http'):
            return href
        from urllib.parse import urljoin
        return urljoin(base_url, href)

    def enrich(self, job_data):
        title = job_data.get('title', '')
        if not job_data.get('last_date'):
            job_data['last_date'] = self.extract_date(title)
        if not job_data.get('total_posts'):
            job_data['total_posts'] = self.extract_post_count(title)
        if not job_data.get('category_slug'):
            job_data['category_slug'] = self.detect_category(title)
        if not job_data.get('state') or job_data.get('state') == 'All India':
            job_data['state'] = self.detect_state(title)
        if not job_data.get('qualification'):
            job_data['qualification'] = self.detect_qualification(title)
        if not job_data.get('job_type') or job_data.get('job_type') == 'latest_jobs':
            job_data['job_type'] = self.detect_job_type(title)
        job_data['source'] = self.source_name
        return job_data

    def scrape(self):
        raise NotImplementedError(f"{self.source_name}.scrape() not implemented")
