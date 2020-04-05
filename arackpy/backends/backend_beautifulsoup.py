
raise NotImplementedError("coming soon")


import urllib2

from bs4 import BeautifulSoup

from arackpy.backends.backend_default import Backend


class Backend_BeautifulSoup(Backend):
    """A more robust and faster html parser but must have bs4 python module
    installed.
    """

    def __init__(self, spider):
        super(Backend_BeautifulSoup, self).__init__(spider)

    def urlread(self, url, timeout):
        return urllib2.urlopen(url, timeout=timeout).read()

    def urlparse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a")
        new_urls = {link.get('href') for link in links}

        return new_urls
