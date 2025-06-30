from scrapers.base import ScraperRegistry
import scrapers.brotherlybud
import scrapers.curaleaf
import scrapers.indigodispensary
import scrapers.mpxnj
import scrapers.shopcuzzies
import time


def main():
    timings = []
    for func in ScraperRegistry.scrapers:
        print(f"Running {func.__name__}()")
        start = time.time()
        func()
        elapsed = time.time() - start
        timings.append((func.__name__, elapsed))
        print(f"{func.__name__} finished in {elapsed:.2f} seconds\n")

    print("\n=== Scraper Timing Summary ===")
    for name, secs in timings:
        print(f"{name}: {secs:.2f} seconds")

if __name__ == "__main__":
    main()