def run_scraper():
    try:
        from scrapers import run_all_scrapers
        return run_all_scrapers()
    except Exception as e:
        print(f"[run_scraper] Error: {e}")
        return 0


def run_quick_scan():
    try:
        from scrapers import run_quick_scan as _quick
        return _quick()
    except Exception as e:
        print(f"[run_quick_scan] Error: {e}")
        return 0


def run_deep_scan():
    try:
        from scrapers import run_deep_scan as _deep
        return _deep()
    except Exception as e:
        print(f"[run_deep_scan] Error: {e}")
        return 0
