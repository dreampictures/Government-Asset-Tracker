import io
import re
import requests

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

DATE_PATTERNS = [
    re.compile(r'(\d{2}[-/]\d{2}[-/]\d{4})'),
    re.compile(r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', re.IGNORECASE),
    re.compile(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', re.IGNORECASE),
]


def download_pdf(url, timeout=20):
    try:
        import random
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/pdf,*/*',
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type.lower() or url.lower().endswith('.pdf'):
                return response.content
    except Exception as e:
        print(f"[PDF] Download error for {url}: {e}")
    return None


def extract_text_from_pdf(pdf_bytes):
    text = ''
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        output = io.StringIO()
        extract_text_to_fp(io.BytesIO(pdf_bytes), output, laparams=LAParams(), output_type='text', codec='utf-8')
        text = output.getvalue()
    except Exception as e:
        print(f"[PDF] pdfminer extraction error: {e}")
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                text += page.extract_text() or ''
        except Exception as e2:
            print(f"[PDF] PyPDF2 extraction error: {e2}")
    return text


def parse_pdf_data(text):
    result = {
        'application_fee': '',
        'age_limit': '',
        'start_date': '',
        'last_date': '',
        'total_posts': '',
        'selection_process': '',
        'eligibility': '',
    }

    if not text:
        return result

    fee_patterns = [
        re.compile(r'(?:application fee|fees?)[^\d]*(?:rs\.?\s*|inr\s*)?(\d[\d,/\-\s]+(?:/-)?)', re.IGNORECASE),
        re.compile(r'(?:general|obc)[^\d]*(?:rs\.?\s*)(\d[\d,]+)', re.IGNORECASE),
    ]
    for pat in fee_patterns:
        m = pat.search(text)
        if m:
            snippet = text[max(0, m.start()-10):m.end()+80].replace('\n', ' ').strip()
            result['application_fee'] = snippet[:300]
            break

    age_patterns = [
        re.compile(r'age\s*limit[^.]*?(\d{2}\s*(?:to|-|–)\s*\d{2,3}\s*years?)', re.IGNORECASE),
        re.compile(r'maximum\s*age[^.]*?(\d{2,3}\s*years?)', re.IGNORECASE),
    ]
    for pat in age_patterns:
        m = pat.search(text)
        if m:
            snippet = text[max(0, m.start()-10):m.end()+80].replace('\n', ' ').strip()
            result['age_limit'] = snippet[:300]
            break

    post_pat = re.compile(r'(\d{2,6})\s*(?:posts?|vacancies|vacancy|openings?)', re.IGNORECASE)
    m = post_pat.search(text)
    if m:
        result['total_posts'] = m.group(1)

    all_dates = []
    for pattern in DATE_PATTERNS:
        all_dates.extend(pattern.findall(text))
    if len(all_dates) >= 2:
        result['start_date'] = all_dates[0]
        result['last_date'] = all_dates[-1]
    elif len(all_dates) == 1:
        result['last_date'] = all_dates[0]

    sel_pat = re.compile(r'selection\s*process[^\n]*?([^\n]{10,300})', re.IGNORECASE)
    m = sel_pat.search(text)
    if m:
        result['selection_process'] = m.group(1).strip()[:300]

    qual_patterns = [
        re.compile(r'(?:educational\s*qualification|eligibility\s*criteria)[^\n]*?([^\n]{10,400})', re.IGNORECASE),
        re.compile(r'qualification[^\n]*?([^\n]{10,300})', re.IGNORECASE),
    ]
    for pat in qual_patterns:
        m = pat.search(text)
        if m:
            result['eligibility'] = m.group(1).strip()[:400]
            break

    return result


def extract_from_pdf_url(url):
    if not url or not url.startswith('http'):
        return {}
    if not url.lower().endswith('.pdf') and 'pdf' not in url.lower():
        return {}
    pdf_bytes = download_pdf(url)
    if not pdf_bytes:
        return {}
    text = extract_text_from_pdf(pdf_bytes)
    if not text:
        return {}
    return parse_pdf_data(text)
