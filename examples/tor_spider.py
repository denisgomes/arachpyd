# tor_spider.py

from __future__ import print_function

from arackpy.spider import Spider


class TorSpider(Spider):
    """A simple spider which uses tor in 10 lines of code."""

    start_urls = ["https://www.cnn.com"]

    timeout = 5

    debug = True

    def __init__(self, backend="Tor", port=9050):
        super(TorSpider, self).__init__(backend)

    def parse(self, url, html):
        """Extract data from the raw html"""
        print("Crawling url, %s" % url)


if __name__ == "__main__":
    print("Press Ctrl-c to stop the crawler")
    spider = TorSpider()
    spider.crawl()
