Writing an **arackpy** application
==================================

Getting started with **arckpy** is easy. This chapter provides a quick intro
without going into too much detail but it effectively touches on everything
you'll need.


Hello, World!
-------------

Open up your favorite python text editor and type the following:

.. code-block:: python

    # hello_spider.py

    from __future__ import division     # for python 2.7

    from arackpy.spider import Spider


    class HelloSpider(Spider):
        """A simple spider in just five lines of working code"""

        start_urls = ["https://www.python.org"]

        def parse(self, url, html):
            """Extract data from the raw html"""
            print("Crawling url, %s" % url)


    if __name__ == "__main__":
        print("Press Ctrl-c to stop crawling")
        spider = HelloSpider()
        spider.crawl()


Run the program using:

.. code-block:: bash

    python hello_spider.py


*See it go!* But wait...! Press Ctrl-c to stop crawling like it says before
reprisal from the BDFL. See the spider API documentation for more information
to better take control of your spider's actions.

.. note::
    You may have to press and hold Ctrl-c for it to work or press Ctrl-c
    multiple times.

**arckpy** is to scrapy what flask is to django. What you do with the url and
the raw html passed to the parse method is up to you to decide. You can parse
the html and do some sort of sentiment analysis or save data into a relational
database like postgresql for later use. It's up to your imagination!

.. note::
    The default behavior of the spider is to parse all urls from the current
    url for the next iteration. The client code may return a list of urls to
    "direct" the spider in a certain path. In addition, if False is returned
    the spider will not add any urls at all from the current url. See the
    follow_trump.py example in the examples directory to see it in action.


Anonymous
---------

**arackpy** can use proxies or tor to crawl and scrape data off the web. The
Hello World spider can be instructed to use proxies by simply specifying the
proxy backend during initialization.

.. code-block:: python

    ...

    class HelloProxySpider(Spider):
        """Using free proxies to crawl"""

        start_urls = ["https://www.python.org"]

        def __init__(self, backend="proxy"):
            super(HelloProxySpider, self).__init__(backend)
        ...

.. note::
    A list of proxies can directly be specified by the user; otherwise a list
    of free proxies is extracted from free-proxy-list.net.

Similarly, using the tor network is just as simple as:

.. code-block:: python

    ...

    class HelloTorSpider(Spider):
        """Using free proxies to crawl"""

        start_urls = ["https://www.python.org"]

        def __init__(self, backend="tor"):
            super(HelloTorSpider, self).__init__(backend)
        ...

.. note::
    You can pass in additional parameters to a backend to customize it. Refer
    to the backend documentation.

.. warning::
    As with all things, **arackpy** does not guarantee complete privacy, so if
    you are being really bad, know what you are doing. Be good!


Where to next?
--------------

Take a look at the **arackpy** examples directory for additional demo programs.
To get the samples, download it from `Github.
<https://www.github.com/denisgomes/arackpy>`_

.. note:: Make sure to get the examples for the version you have installed.
