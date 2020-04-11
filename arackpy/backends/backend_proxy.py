"""Give the spider the ability to access an url via a proxy server to avoid
basic detection. The proxy backend should only be used for low stakes jobs.

If the user does not provide a list of proxies, free proxies from free-proxy-
list is used. Note, free proxies are less dependable and potentially can be
risky so use at your own risk. Free proxies may die out pretty quickly so the
list of proxies should be continually refreshed. Using header spoofing and
rotation will ensure better overall success.

Each thread uses a different proxy to read each url from the group. If the url
cannot be read, either the proxy is dead or the server is not responding. If
the proxy is not working it is removed from the queue. If the proxy queue ever
becomes empty the spider will stop crawling and terminate. If the timer is
reached, the queue is refreshed with new free proxies.

Using free proxies tends to be slow as the quality of the server is usually not
the best.


.. todo::

    Update proxy to AnchorTagParser similar to default_backend AnchorTagParser.
    Convert / to the an absolute url.

    Allow the user to specify a free proxy website and a function to extract
    the proxy information that website.
"""

from __future__ import print_function
import logging
import threading
import time
import sys

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

import requests
from lxml.html import fromstring

from fake_useragent import UserAgent

from arackpy.backends.backend_default import Backend


class AnchorTagParser(object):

    def parse(self, html):
        parser = fromstring(html)
        urls = parser.xpath("//a/@href")

        return urls


def get_free_proxies():
    # https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
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

        self.ua = UserAgent()

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
        user_agent = self.ua.random
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
                logging.info("adding proxy %s back into queue" % proxy)
                self.proxies.put(proxy)

                return html
            except:     # bad proxy / bad server / etc
                # print("testing proxy %s" % proxy)
                # self._test_proxy(url, proxy, timeout)
                return self.urlread(url, timeout)

        except Queue.Empty:
            # wait for all threads to join when queue is empty
            while threading.active_count() > 1:
                time.sleep(0.1)

            # refill queue if using free proxies
            # if self._user_proxies:
            logging.error("proxy list exhausted, spider stopped")
            sys.exit()
            # else:
            #     self.proxies = get_free_proxies()

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
