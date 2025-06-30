class ScraperRegistry:
    scrapers = []

    @classmethod
    def register(cls, scraper_func):
        cls.scrapers.append(scraper_func)
        return scraper_func
