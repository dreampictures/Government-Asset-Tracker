from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class IBPSScraper(BaseScraper):
    BASE_URL = 'https://www.ibps.in'

    def __init__(self):
        super().__init__('ibps')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_recruitment())
            jobs.extend(self._scrape_updates())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _scrape_recruitment(self):
        jobs = []
        urls = [
            f'{self.BASE_URL}/ibps-recruitment/',
            f'{self.BASE_URL}/ibps-notification/',
            f'{self.BASE_URL}/',
        ]
        for url in urls:
            response = self.safe_request(url)
            if not response:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            selectors = ['article a', 'h2 a', 'h3 a', '.entry-title a', 'td a', 'li a']
            for sel in selectors:
                for a in soup.select(sel):
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    if not title or len(title) < 10:
                        continue
                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in ['ibps', 'recruitment', 'notification', 'po', 'clerk', 'rrb', 'specialist', 'admit', 'result', 'answer key']):
                        continue
                    full_href = self.build_absolute_url(href, self.BASE_URL)
                    pdf_link = full_href if '.pdf' in full_href.lower() else ''
                    job = {
                        'title': title,
                        'organization': 'Institute of Banking Personnel Selection',
                        'apply_link': full_href if not pdf_link else self.BASE_URL,
                        'notification_link': pdf_link,
                        'last_date': self.extract_date(title),
                        'total_posts': self.extract_post_count(title),
                        'qualification': 'Graduation',
                        'state': 'All India',
                        'category_slug': 'bank-jobs',
                        'job_type': self.detect_job_type(title),
                    }
                    jobs.append(self.enrich(job))
                    if len(jobs) >= 12:
                        break
                if jobs:
                    break
            if jobs:
                break
        return jobs[:12]

    def _scrape_updates(self):
        jobs = []
        url = f'{self.BASE_URL}/important-dates/'
        response = self.safe_request(url)
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True)[:20]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 10:
                continue
            title_lower = title.lower()
            if not any(kw in title_lower for kw in ['ibps', 'admit', 'result', 'interview', 'exam']):
                continue
            full_href = self.build_absolute_url(href, self.BASE_URL)
            job = {
                'title': title,
                'organization': 'Institute of Banking Personnel Selection',
                'apply_link': self.BASE_URL,
                'notification_link': full_href if '.pdf' in full_href.lower() else '',
                'last_date': self.extract_date(title),
                'total_posts': '',
                'qualification': 'Graduation',
                'state': 'All India',
                'category_slug': 'bank-jobs',
                'job_type': self.detect_job_type(title),
            }
            jobs.append(self.enrich(job))
            if len(jobs) >= 8:
                break
        return jobs
