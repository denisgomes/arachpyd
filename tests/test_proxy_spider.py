from __future__ import print_function

import unittest

# relative import - unittest to start doc server
from tests.basetest import (TestSpider, TestCaseSpider, setUpModule,
                            PROXY_SERVER_PORT)


class ProxySpider(TestSpider):

    debug = True

    # do not use total_url_count
    count = 0

    def parse(self, url, html):
        # print("Crawling url, %s" % url)
        ProxySpider.count += 1


class TestProxySpider(TestCaseSpider):
    """Use a proxy to query the pydocs server running on localhost."""

    def setUp(self):
        proxies = ["localhost:%s" % PROXY_SERVER_PORT]
        self.spider = ProxySpider("proxy", proxies=proxies)

    def tearDown(self):
        del self.spider

    def test_max_urls(self):
        """Test to see if 'max_urls' is met"""
        self.spider.crawl(5)
        self.assertEqual(self.spider.count, 5)

    def test_max_urls_2(self):
        """Test for one off error"""
        self.spider.crawl(5)
        self.assertNotEqual(self.spider.count, 6)

    def test_max_urls_3(self):
        """Test for one off error"""
        self.spider.crawl(5)
        print(self.spider.count)
        self.assertNotEqual(self.spider.count, 4)


if __name__ == "__main__":
    unittest.main()
