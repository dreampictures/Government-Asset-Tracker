from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class RailwayScraper(BaseScraper):
    def __init__(self):
        super().__init__('railway')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_rrb())
            jobs.extend(self._scrape_rrc())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _scrape_rrb(self):
        jobs = []
        urls = [
            'https://www.rrbcdg.gov.in/',
            'https://www.rrbald.gov.in/',
            'https://indianrailways.gov.in/',
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
                if not any(kw in title_lower for kw in ['recruitment', 'vacancy', 'notification', 'ntpc', 'rrb', 'admit', 'result', 'answer key', 'alp', 'group d', 'technician']):
                    continue
                full_href = self.build_absolute_url(href, url)
                pdf_link = full_href if '.pdf' in full_href.lower() else ''
                job = {
                    'title': title,
                    'organization': 'Railway Recruitment Board',
                    'apply_link': full_href if not pdf_link else url,
                    'notification_link': pdf_link,
                    'last_date': self.extract_date(title),
                    'total_posts': self.extract_post_count(title),
                    'qualification': self.detect_qualification(title),
                    'state': 'All India',
                    'category_slug': 'railway-jobs',
                    'job_type': self.detect_job_type(title),
                }
                jobs.append(self.enrich(job))
                if len(jobs) >= 10:
                    break
            if jobs:
                break
        return jobs[:10]

    def _scrape_rrc(self):
        jobs = []
        url = 'https://www.rrcb.gov.in/'
        response = self.safe_request(url)
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True)[:30]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 15:
                continue
            title_lower = title.lower()
            if not any(kw in title_lower for kw in ['recruitment', 'vacancy', 'notification', 'admit', 'result']):
                continue
            full_href = self.build_absolute_url(href, url)
            job = {
                'title': title,
                'organization': 'Railway Recruitment Cell',
                'apply_link': full_href,
                'notification_link': '',
                'last_date': self.extract_date(title),
                'total_posts': self.extract_post_count(title),
                'qualification': self.detect_qualification(title),
                'state': 'All India',
                'category_slug': 'railway-jobs',
                'job_type': self.detect_job_type(title),
            }
            jobs.append(self.enrich(job))
            if len(jobs) >= 8:
                break
        return jobs
