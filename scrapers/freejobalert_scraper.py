from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class FreeJobAlertScraper(BaseScraper):
    BASE_URL = 'https://www.freejobalert.com'

    def __init__(self):
        super().__init__('freejobalert')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_notifications())
            jobs.extend(self._scrape_admit_cards())
            jobs.extend(self._scrape_results())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _scrape_notifications(self):
        jobs = []
        response = self.safe_request(f'{self.BASE_URL}/latest-notifications/page/1/')
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table tr')
        for row in rows[:30]:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            link = cells[0].find('a')
            if not link:
                continue
            title = link.get_text(strip=True)
            href = link.get('href', '')
            last_date = cells[-1].get_text(strip=True) if len(cells) > 1 else ''
            if not title or len(title) < 10:
                continue
            job = {
                'title': title,
                'organization': self.extract_org_from_title(title),
                'apply_link': href if href.startswith('http') else '',
                'notification_link': '',
                'last_date': last_date[:20] if last_date else '',
                'total_posts': '',
                'qualification': '',
                'state': 'All India',
                'category_slug': None,
                'job_type': 'latest_jobs',
            }
            jobs.append(self.enrich(job))
        return jobs

    def _scrape_admit_cards(self):
        jobs = []
        response = self.safe_request(f'{self.BASE_URL}/admit-card/')
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.select('h3 a, .entry-title a, article a')[:15]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 10:
                continue
            job = {
                'title': title,
                'organization': self.extract_org_from_title(title),
                'apply_link': href if href.startswith('http') else '',
                'notification_link': '',
                'last_date': '',
                'total_posts': '',
                'qualification': '',
                'state': 'All India',
                'category_slug': None,
                'job_type': 'admit_card',
            }
            jobs.append(self.enrich(job))
        return jobs

    def _scrape_results(self):
        jobs = []
        response = self.safe_request(f'{self.BASE_URL}/results/')
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.select('h3 a, .entry-title a, article a')[:15]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if not title or len(title) < 10:
                continue
            job = {
                'title': title,
                'organization': self.extract_org_from_title(title),
                'apply_link': href if href.startswith('http') else '',
                'notification_link': '',
                'last_date': '',
                'total_posts': '',
                'qualification': '',
                'state': 'All India',
                'category_slug': None,
                'job_type': 'result',
            }
            jobs.append(self.enrich(job))
        return jobs
