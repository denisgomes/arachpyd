Writing an **arackpy** application
==================================

Getting started with a new library or framework can be daunting, especially
when presented with a large amount of reference material to read.  This chapter
gives a very quick introduction to **arackpy** without going into too much
detail.


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
reprisal from the BDFL. See the API documentation for more information to
better take control of your spider's actions.

.. note:: You may have to press and hold Ctrl-c for it to work.


Anonymous
---------

**arackpy** can use proxies or tor to crawl and scrape data off the web. The
Hello World spider can be instructed to use proxies by simply specifying the
Proxy backend during initialization.

.. code-block:: python

    ...

    class HelloProxySpider(Spider):
        """Using free proxies to crawl"""

        start_urls = ["https://www.python.org"]

        def __init__(self, backend="Proxy"):
            super(HelloProxySpider, self).__init__(backend)

        ...

Similarly, using the tor network is just as simple as:

.. code-block:: python

    ...

    class HelloTorSpider(Spider):
        """Using free proxies to crawl"""

        start_urls = ["https://www.python.org"]

        def __init__(self, backend="Tor"):
            super(HelloTorSpider, self).__init__(backend)

        ...

.. note:: You can pass in additional parameters to a backend to customize it.
          Refer to the backend documentation.

.. warning:: As with all things, **arackpy** does not guarantee full proof
             privacy, so if you are being really bad, know what you are doing.


Where to next?
--------------

Take a look at the **arackpy** examples directory for additional demo programs.
To get the samples, download it from `BitBucket.
<https://bitbucket.org/denisgomes/arackpy>`_

.. note:: Make sure to get the examples for the version you have installed.
