.. arackpy documentation master file, created by
   sphinx-quickstart on Mon Jun 17 19:58:14 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Overview
========

**arackpy** is a simple but powerful web crawler and scraper. While it is good
natured and respectful by default, it can be used to do evil. Remember with
great power comes great responsibility.

Some features of **arackpy** are:

    1. Concurrent page downloads using Python threads

    2. Support for robots.txt to prevent host server bottlenecking

    3. Different backends for additional capabilities such as:

        a. Anonymous scraping using proxies and tor.

        b. Dealing with JavaScript/AJAX requests and,

Join us on the mailing list. Coming soon!


Requirements
------------

**arackpy** currently supports Python 2.7 and 3.6+ out of the box. Depending on
the data you want to extract, **future** releases will require one or more of
the dependencies below to be installed to support the various backends:

* beautifulSoup and lxml
* requests
* pysocks
* fake_useragent
* selenium


Installation
------------

For the vanilla **arackpy** install do a simple pip install:


.. code-block:: bash

    pip install arackpy

The following packages may also be installed:

.. code-block:: bash

    pip install bs4, lxml, requests, pysocks, fake_useragent, selenium


Quickstart
----------

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

.. note:: Press Ctrl-c to terminate crawling.


Programming Guide
=================

The **arackpy** Programming Guide provides in-depth documentation for writing
applications using **arackpy**. Many topics described here reference the
**arackpy** API reference, which is listed below.

If this is your first time reading about **arackpy**, we suggest you start at
:doc:`programming_guide/quickstart`.

.. toctree::
   :maxdepth: 2

   programming_guide/installation.rst
   programming_guide/quickstart.rst


API Reference
=============

.. toctree::
   :maxdepth: 2

   modules/spider.rst


Developer Guide
===============

These documents describe details on how to develop **arackpy** itself further.
Ready these to get a more detailed insight into how **arackpy** is designed,
and how to help make **arackpy** even better. Get in touch if you would like to
contribute!


.. toctree::
   :maxdepth: 2

   internal/virtualenv.rst
   internal/testing.rst
   internal/docs.rst
   internal/workflow.rst


Related Documentation
=====================

* `Python Documentation <http://docs.python.org/>`_


Third Party Libraries
=====================

Listed here are a few third party libraries that you might find useful when
developing your projects. Please direct any questions to the respective
authors.

* `BeautifulSoup - A Python library for pulling data out of HTML and XML files.
  <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_

    Works well with static websites where all content is loaded at one time. If installed **arackpy** uses bs4 to extract anchor tags from html pages.

* For Tor backed anonymous scraping, the following libraries are required.
    * `Requests - HTTP for Humans. <https://2.python-requests.org/en/master/>`_
    * `PySocks - A SOCKS proxy client and wrapper for Python. <https://github.com/Anorov/PySocks>`_
    * `Fake_UserAgent - Up to date simple useragent faker with real world
      database. <https://github.com/hellysmile/fake-useragent>`_

* `Selenium - A webdriver and test automation tool.
  <https://selenium-python.readthedocs.io/>`_

    Works well with websites that use javascript and AJAX to dynamically update different sections of the website.
