try:
    from HTMLParser import HTMLParser
    import urllib2
    from urlparse import urlsplit, urljoin
except ImportError:
    from html.parser import HTMLParser
    from urllib.parse import urlsplit, urljoin


def is_absolute(url):
    # https://stackoverflow.com/questions/8357098/how-can-i-check-if-a-url-is-absolute-using-python
    return bool(urlsplit(url).netloc)


def urlopentorr(url):
    proxy_support = urllib2.ProxyHandler({"http": "127.0.0.1:8118"})
    opener = urllib2.build_opener(proxy_support)
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    return opener.open(url).read()


class AnchorTagParser(HTMLParser):
    """Native url anchor tag parser"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.urls.add(value)

    def parse(self, html):
        """Parse and extract all anchor tags"""
        self.feed(html)
        urls = self.urls.copy()
        self.urls.clear()

        # print urls

        return urls
