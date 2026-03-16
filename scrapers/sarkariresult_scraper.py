from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class SarkariResultScraper(BaseScraper):
    BASE_URL = 'https://www.sarkariresult.com'

    def __init__(self):
        super().__init__('sarkariresult')

    def scrape(self):
        jobs = []
        try:
            jobs.extend(self._scrape_latest())
            jobs.extend(self._scrape_admit_cards())
            jobs.extend(self._scrape_results())
            jobs.extend(self._scrape_answer_keys())
        except Exception as e:
            print(f"[{self.source_name}] Error: {e}")
        print(f"[{self.source_name}] Found {len(jobs)} items")
        return jobs

    def _parse_table_links(self, url, job_type='latest_jobs', limit=25):
        jobs = []
        response = self.safe_request(url)
        if not response:
            return jobs
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('td a[href]')
        for link in links[:limit]:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if not title or len(title) < 10 or not href:
                continue
            full_href = self.build_absolute_url(href, self.BASE_URL)
            job = {
                'title': title,
                'organization': self.extract_org_from_title(title),
                'apply_link': full_href,
                'notification_link': '',
                'last_date': '',
                'total_posts': '',
                'qualification': '',
                'state': 'All India',
                'category_slug': None,
                'job_type': job_type,
            }
            jobs.append(self.enrich(job))
        return jobs

    def _scrape_latest(self):
        return self._parse_table_links(f'{self.BASE_URL}/latestjob.php', 'latest_jobs', 25)

    def _scrape_admit_cards(self):
        return self._parse_table_links(f'{self.BASE_URL}/admit.php', 'admit_card', 15)

    def _scrape_results(self):
        return self._parse_table_links(f'{self.BASE_URL}/result.php', 'result', 15)

    def _scrape_answer_keys(self):
        return self._parse_table_links(f'{self.BASE_URL}/answerkey.php', 'answer_key', 10)
