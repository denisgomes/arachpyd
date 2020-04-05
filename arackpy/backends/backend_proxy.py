"""Give the spider the ability to access an url via a proxy server to avoid
basic detection. The proxy backend should only be used for low stakes jobs.

If the user does not provide a list of proxies, free proxies from free-proxy-
list is used. Note, free proxies are less dependable and potentially can be
risky so use at your own risk. Free proxies may die out pretty quickly so the
list of proxies should be continually refreshed. Using header spoofing and
rotation will ensure better overall success.

Each thread uses a different proxy to read each url from the group. If the url
cannot be read, either the proxy is dead or the server is not responding. If
the proxy is not working it is removed from the queue. If the queue ever
becomes empty or if the timer is reached, the queue is refreshed with new free
proxies. If however the proxies were user specified, the spider will stop
crawling and exit.

Using free proxies tends to be slow as the quality of the server is usually not
the best.
"""

from __future__ import print_function
import logging
import threading
import time
import random
import sys

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

import requests
from lxml.html import fromstring

from arackpy.backends.backend_default import Backend


USER_AGENT_LIST = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]


class AnchorTagParser(object):

    def parse(self, html):
        parser = fromstring(html)
        urls = parser.xpath("//a/@href")

        return urls

# https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
def get_free_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)

    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)

    queue = Queue()
    for proxy in proxies:
        queue.put(proxy)

    return queue


class Backend_Proxy(Backend):
    """Backend which handles user defined or free proxies for different each
    url.

    :Parameters:
        `proxies` : list
            List of user defined proxies and corresponding ports separated by
            a colon.

        `update_timer` : int
            Define the time in minutes after which the free proxy queue is
            refreshed. Only applies to free proxies.
    """
    def __init__(self, spider, proxies=None, update_timer=5):
        super(Backend_Proxy, self).__init__(spider)

        if proxies:
            self._user_proxies = True
            self.proxies = Queue()
            for proxy in proxies:
                self.proxies.put(proxy)
        else:
            self._user_proxies = False
            logging.warning("using free proxies from free-proxy-list.net")
            self.proxies = get_free_proxies()
            self.proxy_updater_thread = threading.Timer(update_timer*60,
                                                        self.clear_proxies)

        self.parser = AnchorTagParser()

    def _test_proxy(self, url, proxy, timeout):
        # is url bad or proxy bad
        try:
            # check if bad proxy - assuming google is good, wink
            test_url = "https://www.google.com"
            resp = requests.head(test_url, proxies=proxy, timeout=timeout)
        except:     # bad proxy
            logging.info("removing proxy %s" % proxy)
        else:
            logging.info("adding proxy %s back to queue" % proxy)
            self.proxies.put(proxy)
        finally:
            # read using another proxy no matter what
            self.urlread(url, timeout)

    def _read(self, url, proxy, timeout):
        proxies = {"http": proxy, "https": proxy}
        user_agent = random.choice(USER_AGENT_LIST)     # randomize
        headers = {"User-Agent": user_agent}
        response = requests.get(url, timeout=timeout, proxies=proxies,
                                headers=headers)
        return response.text

    def urlread(self, url, timeout):
        try:
            # grab from queue
            proxy = self.proxies.get(timeout=0.1)
            # print("Reading %s using proxy %s" % (url, proxy))

            try:
                html = self._read(url, proxy, timeout)
                logging.info("adding proxy back into queue")
                self.proxies.put(proxy)

                return html
            except:     # bad proxy / bad server / etc

                # print("testing proxy %s" % proxy)

                self._test_proxy(url, proxy, timeout)

        except Queue.Empty:
            # wait for all threads to join when queue is empty
            while threading.active_count() > 1:
                time.sleep(0.1)

            # refill queue if using free proxies
            if self._user_proxies:
                logging.error("proxy list is empty, spider stopped")
                sys.exit()
            else:
                self.proxies = get_free_proxies()

    def urlparse(self, html):
        return self.parser.parse(html)

    def clear_proxies(self):
        """Empty the proxy queue so that new proxies are loaded.

        After the queue is emptied, the next call to urlread by a thread throws
        an empty queue error. This occurs until the thread count drops to 1 and
        only the main thread is active. At this point the queue is refilled.
        """
        logging.info("clearing the proxy queue")
        # these queue methods are undocumented
        with self.proxies.mutex:
            self.proxies.queue.clear()

