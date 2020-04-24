arackpy.backends
================

Backends allow **arackpy** to crawl the web in differnt ways. For example, the
proxy backend uses proxy servers whereas the tor backend ventures across the
tor network.

The type of backend to use is passed in as an input argument to the Spider
dunder init method. In addition, backend specific input arguments can be
specified as shown in the example below:

.. code-block:: python

    # proxy spider with arguments

    from __future__ import print_function

    from aracky.spider import Spider


    class ProxySpider(Spider):
        """A simple hello world proxy spider.

        Spider uses free proxies and refreshes rotating proxy list every 10
        minutes.
        """

        start_urls = ["https://www.python.org"]

        def __init__(self, backend="proxy", update_timer=10):
            super(ProxySpider, self).__init__(backend=backend,
                                              update_timer=update_timer)

        def parse(self, url, html):
            """Extract data from the raw html"""
            print("Crawling url, %s using proxy" % url)


.. attention::
    Carefully study and apply the input arguments for the various backends to
    achieve the desired behavior.

backend_default.Backend_Default
-------------------------------

.. automodule:: arackpy.backends.backend_default

.. autoclass:: Backend_Default


backend_proxy.Backend_Proxy
---------------------------

.. automodule:: arackpy.backends.backend_proxy

.. autoclass:: Backend_Proxy


backend_tor.Backend_Tor
-----------------------

.. automodule:: arackpy.backends.backend_tor

.. autoclass:: Backend_Tor
