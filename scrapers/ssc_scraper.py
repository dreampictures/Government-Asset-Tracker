from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class SSCScraper(BaseScraper):
    BASE_URL = 'https://ssc.nic.in'

    def __init__(self):
        super().__init__('ssc')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_recruitment())
            jobs.extend(self._scrape_results())
            jobs.extend(self._scrape_admit_cards())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _scrape_recruitment(self):
        jobs = []
        urls = [
            f'{self.BASE_URL}/',
            f'{self.BASE_URL}/notices',
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
                if not any(kw in title_lower for kw in ['recruitment', 'vacancy', 'notification', 'advertisement', 'admit', 'result', 'answer key']):
                    continue
                full_href = self.build_absolute_url(href, self.BASE_URL)
                job_type = self.detect_job_type(title)
                pdf_link = full_href if full_href.lower().endswith('.pdf') else ''
                job = {
                    'title': title,
                    'organization': 'Staff Selection Commission',
                    'apply_link': full_href if not pdf_link else self.BASE_URL,
                    'notification_link': pdf_link,
                    'last_date': self.extract_date(title),
                    'total_posts': self.extract_post_count(title),
                    'qualification': self.detect_qualification(title),
                    'state': 'All India',
                    'category_slug': 'central-govt-jobs',
                    'job_type': job_type,
                }
                jobs.append(self.enrich(job))
                if len(jobs) >= 15:
                    break
            if jobs:
                break
        return jobs[:15]

    def _scrape_results(self):
        return self._scrape_by_type('/result', 'result', 10)

    def _scrape_admit_cards(self):
        return self._scrape_by_type('/admit', 'admit_card', 10)

    def _scrape_by_type(self, path, job_type, limit):
        jobs = []
        response = self.safe_request(f'{self.BASE_URL}{path}')
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True)[:limit * 2]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 10:
                continue
            full_href = self.build_absolute_url(href, self.BASE_URL)
            job = {
                'title': title,
                'organization': 'Staff Selection Commission',
                'apply_link': self.BASE_URL,
                'notification_link': full_href if full_href.lower().endswith('.pdf') else '',
                'last_date': self.extract_date(title),
                'total_posts': '',
                'qualification': '',
                'state': 'All India',
                'category_slug': 'central-govt-jobs',
                'job_type': job_type,
            }
            jobs.append(self.enrich(job))
            if len(jobs) >= limit:
                break
        return jobs
