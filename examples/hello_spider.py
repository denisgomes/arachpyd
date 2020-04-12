# hello_spider.py

from __future__ import print_function

from arackpy.spider import Spider


class HelloSpider(Spider):
    """A simple spider in just five lines of working code"""

    wait_time_range = (1, 3)

    start_urls = ["https://www.msn.com"]

    max_urls_per_level = 5

    follow_external_links = True

    debug = True

    def parse(self, url, html):
        """Extract data from the raw html"""
        print("Crawling url, %s" % url)


if __name__ == "__main__":
    print("Press Ctrl-c to stop the crawler")
    spider = HelloSpider()
    spider.crawl()
