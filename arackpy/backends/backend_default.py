"""Pure Python backend for reading html and extracting urls."""


from __future__ import print_function

from abc import abstractmethod

try:
    import urllib2
except ImportError:
    import urllib.request
    import urllib.error
    import urllib.parse

from arackpy.utils import AnchorTagParser


class Backend(object):
    """Abstract base class"""

    def __init__(self, spider):
        self.spider = spider

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def urlread(self, url, timeout):
        """Return the raw html data"""
        pass

    @abstractmethod
    def urlparse(self, html):
        """Return a set of urls"""
        pass


class Backend_Default(Backend):
    """The default backend uses urllib2 to download html and the native Python
    html parser to extract all anchor tags. This method can be slow and may not
    extract urls for all links with success.
    """

    def __init__(self, spider):
        super(Backend_Default, self).__init__(spider)
        self.parser = AnchorTagParser()

    def urlread(self, url, timeout):
        try:
            return urllib2.urlopen(url, timeout=timeout).read().decode("utf-8")
        except NameError:
            # py3
            response = urllib.request.urlopen(url, timeout=timeout)
            return response.read().decode("utf-8")

    def urlparse(self, html):
        return self.parser.parse(html)
