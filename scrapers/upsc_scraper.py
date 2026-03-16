from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class UPSCScraper(BaseScraper):
    BASE_URL = 'https://upsc.gov.in'

    def __init__(self):
        super().__init__('upsc')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_examinations())
            jobs.extend(self._scrape_results())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _scrape_examinations(self):
        jobs = []
        urls = [
            f'{self.BASE_URL}/examinations/examination',
            f'{self.BASE_URL}/examinations/active-examinations',
            f'{self.BASE_URL}/',
        ]
        for url in urls:
            response = self.safe_request(url)
            if not response:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a.get('href', '')
                if not title or len(title) < 15:
                    continue
                title_lower = title.lower()
                if not any(kw in title_lower for kw in ['examination', 'recruitment', 'vacancy', 'notification', 'civil services', 'ias', 'ips', 'admit', 'result']):
                    continue
                full_href = self.build_absolute_url(href, self.BASE_URL)
                pdf_link = full_href if '.pdf' in full_href.lower() else ''
                job = {
                    'title': title,
                    'organization': 'Union Public Service Commission',
                    'apply_link': full_href if not pdf_link else self.BASE_URL,
                    'notification_link': pdf_link,
                    'last_date': self.extract_date(title),
                    'total_posts': self.extract_post_count(title),
                    'qualification': 'Graduation',
                    'state': 'All India',
                    'category_slug': 'central-govt-jobs',
                    'job_type': self.detect_job_type(title),
                }
                jobs.append(self.enrich(job))
                if len(jobs) >= 10:
                    break
            if jobs:
                break
        return jobs[:10]

    def _scrape_results(self):
        jobs = []
        url = f'{self.BASE_URL}/examinations/written-result'
        response = self.safe_request(url)
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True)[:20]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 10:
                continue
            full_href = self.build_absolute_url(href, self.BASE_URL)
            job = {
                'title': title,
                'organization': 'Union Public Service Commission',
                'apply_link': self.BASE_URL,
                'notification_link': full_href if '.pdf' in full_href.lower() else '',
                'last_date': '',
                'total_posts': '',
                'qualification': 'Graduation',
                'state': 'All India',
                'category_slug': 'central-govt-jobs',
                'job_type': 'result',
            }
            jobs.append(self.enrich(job))
            if len(jobs) >= 8:
                break
        return jobs
