from __future__ import print_function

from collections import Counter

from bs4 import BeautifulSoup
from bs4.element import Comment

from arackpy.spider import Spider


def tag_visible(element):
    if element.parent.name in ["style", "script", "head", "title", "meta",
                               "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def hrefs_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    hrefs = [a["href"] for a in soup.findAll("a", href=True)]

    return hrefs


class FollowTrumpSpider(Spider):
    """Crawls the web for links that mention Trump in the body."""

    start_urls = ["https://news.yahoo.com", "https://news.cnn.com"]

    wait_time_range = (1, 3)

    timeout = 3

    max_urls_per_level = 50

    # debug = True

    def parse(self, url, html):
        text = text_from_html(html)
        count = Counter(text.lower().split())

        if count["trump"] >= 1:
            print("Following Trump at %s"
                  " - (%s) mentions." % (url, count["trump"]))
            hrefs = hrefs_from_html(html)

            # list of urls to put on queue
            return hrefs

        return False    # only follow trump


if __name__ == "__main__":
    spider = FollowTrumpSpider()
    spider.crawl()
