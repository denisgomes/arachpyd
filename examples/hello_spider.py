# hello_spider.py

from __future__ import print_function

from arackpy.spider import Spider


class HelloSpider(Spider):
    """A simple spider in just five lines of working code"""

    start_urls = ["https://www.yahoo.com"]

    def parse(self, url, html):
        """Extract data from the raw html"""
        print("Crawling url, %s" % url)


if __name__ == "__main__":
    print("Press Ctrl-c to stop the crawler")
    spider = HelloSpider()
    spider.crawl()
