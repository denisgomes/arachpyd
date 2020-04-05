"""Use Tor to scrape websites.

Remember to still respect the server!

# https://medium.com/@jasonrigden/using-tor-with-the-python-request-library-79015b2606cb

1. Make sure tor is installed.

$ sudo apt install tor

2. Install requests, pysocks and fake_useragent

$ pip install requests, pysocks, fake_useragent

try this is you have problems with crpytography
sudo apt install build-essential libssl-dev libffi-dev python-dev

"""
from __future__ import print_function

import requests
from lxml.html import fromstring

from fake_useragent import UserAgent

from arackpy.backends.backend_default import Backend


class AnchorTagParser(object):

    def parse(self, html):
        parser = fromstring(html)
        urls = parser.xpath("//a/@href")

        return urls


class Backend_Tor(Backend):
    """Allows for the Tor protocol to anonymously crawl pages.

    :Parameters:
        `port` : int
            Port on which the tor service is running, defaults to 9050.
    """
    def __init__(self, spider, port=9050):
        self.ua = UserAgent()

        self.s = requests.Session()
        self.s.proxies["http"] = "socks5h://localhost:%s" % port
        self.s.proxies["https"] = "socks5h://localhost:%s" % port

        self.parser = AnchorTagParser()

    def urlread(self, url, timeout):
        user_agent = self.ua.random
        headers = {"User-Agent": user_agent}
        response = self.s.get(url, timeout=timeout, headers=headers)

        return response.text

    def urlparse(self, html):
        return self.parser.parse(html)
