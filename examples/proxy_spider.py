# proxy_spider.py

from __future__ import print_function

from arackpy.spider import Spider


class ProxySpider(Spider):
    """A simple spider which uses proxies in 5 lines of code.

    It updates the proxy queue every 10 minutes with new proxies.
    """

    start_urls = ["https://www.cnn.com"]

    timeout = 3

    debug = True

    def __init__(self, backend="proxy", update_timer=10):
        super(ProxySpider, self).__init__(backend=backend,
                                          update_timer=update_timer)

    def parse(self, url, html):
        """Extract data from the raw html"""
        print("Crawling url, %s" % url)


if __name__ == "__main__":
    print("Press Ctrl-c to stop the crawler")
    spider = ProxySpider()
    spider.crawl()
