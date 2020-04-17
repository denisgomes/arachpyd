"""A multithreaded web crawler and scraper."""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

from abc import abstractmethod
from collections import deque, defaultdict
import logging

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full

import random

try:
    from robotparser import RobotFileParser
except ImportError:
    from urllib.robotparser import RobotFileParser

import sys
from socket import gethostbyname
import time
import threading

try:
    from urlparse import urlsplit, urljoin
except ImportError:
    from urllib.parse import urlsplit, urljoin


from arackpy.backends.backend_default import Backend_Default

# change default encoding for py27 from ascii
if sys.version_info <= (2, 7):
    reload(sys)
    sys.setdefaultencoding("utf8")


# report critial levels above 'warning', (i.e. 'error' and 'critical'), default
logging.basicConfig(level=logging.ERROR)

# mapping between name and class
BACKENDS = {"default": Backend_Default,
            "proxy": None,
            "tor": None,
            "selenium": None,
            }

try:
    from arackpy.backends.backend_proxy import Backend_Proxy
    BACKENDS["proxy"] = Backend_Proxy
except ImportError as e:
    logging.error("Unable to import backend %s" % "proxy")

try:
    from arackpy.backends.backend_tor import Backend_Tor
    BACKENDS["tor"] = Backend_Tor
except NotImplementedError as e:
    logging.warning("Unable to import backend %s" % "tor")


class Spider(object):
    """Create a spider.

    The spider is implemented using two queues. Reader threads get from the
    active queue and put into the empty queue. When the active queue is empty,
    it is swapped with the once empty but now full queue. New reader threads
    are spawned at every level and process urls from the active queue.

    Urls are grouped by host server ip address and the corresponding html is
    downloaded sequentially from each ip depending on the requirements set in
    the robots.txt file. If a time duration is not explicitly specified in the
    robots file, the default wait_time_range is used.

    The spider can be terminated based on two parameters, namely max_urls and
    max_levels. Pressing Ctrl-c will also interrupt and kill the spider albeit
    in a harsh manner.

    :Parameters:
        `start_urls` : list
            List of urls marking the starting point for the spider.

        `follow_external_links` : bool
            If set to True, spider will traverse domains outside the starting
            urls.

        `visit_history_limit` : int
            Used to set the cache size of the deque which keeps tracks of all
            the visisted urls.

        `respect_server` : bool
            If set to True, the wait_time_range attribute is applied.

        `read_robots_file` : bool
            If set to True, the robots.txt file is parsed and checked. The
            spider honors the time and/or download rate as well as whether
            to crawl the page at all. If a time cannot be determined, the
            wait_time_range is set to the default.

        `wait_time_range` : tuple
            A time interval from which a wait time is randomly selected.

        `timeout` : int
            The timeout used when the url is read from. If the url cannot be
            read within the specified time, a timeout exception occurs.

        `thread_safe_parse` : bool
            If set to True, the parse method is thread safe, which allows for
            easy debugging using print statements.

        `max_urls_per_level` : int
            Children urls immediately below the start urls form the first
            level. Since the number of urls per level can increase at an
            exponential rate, a limit is set to prevent memory bottlenecks by
            defining a max queue size for the active and empty queues.

        `max_level` : int
            The maximum number of levels to crawl before termination. Everytime
            all the reader threads return (i.e. join), marks the end of the
            previous level and the beginning of the next.

        `max_urls` : int
            The total number of urls to crawl before termination. This is
            implemented using a counter that each reader thread increments
            by one after it reads an url.

        `debug` : bool
            Log all debug messages to stdout.

        `backend` : Backend
            The type of backend to use for the spider. The default backend is
            specified if nothing is specified. See below for a list of other
            backend and their specific use cases.

        `kwargs` : dict
            Keyword arguments used to initialize the specific backend.

    TODO

        In order of importance:

        1. Implement a bloomfilter for visisted urls cache instead of a deque.

    BUGS

        1. Pypi not showing code syntax highlighting.

    """
    # specify one or more website domain names
    start_urls = []

    # stay at the same top level domain
    follow_external_links = False

    # TODO: implement a bloomfilter
    visit_history_limit = 2000

    # be nice to the host server
    respect_server = True

    read_robots_file = True

    wait_time_range = (1, 3)

    # urlopen timeout in seconds
    timeout = 1

    # thread safe parse
    thread_safe_parse = True

    # max urls to put on queue every jump
    max_urls_per_level = 1000

    # termination criteria
    max_levels = 100    # max jumps
    max_urls = 5000     # total urls

    # debug mode
    debug = False

    def __init__(self, backend="default", **kwargs):
        """Create a spider instance using a backend. The 'default' backend is
        used by default.

        :Parameters:
            `backend` : str
                The type of backend to use.

            **kwargs
                Backend specific arguments.
        """
        assert len(self.start_urls) <= self.max_urls_per_level

        # level implementation using queues
        self.active_queue = Queue(self.max_urls_per_level)
        self.empty_queue = Queue(self.max_urls_per_level)

        # top level domain names
        self.tlds = [self.get_tld(url) for url in self.start_urls]

        self.visited = deque(maxlen=self.visit_history_limit)

        self.lock = threading.Lock()

        # termination flags
        self.level = 0
        self.total_url_count = 0

        # backends for reading html and extracting urls
        try:
            self.backend = BACKENDS[backend](self, **kwargs)
        except (KeyError, TypeError):
            self.backend = BACKENDS["default"](self)
            logging.warning("Using backend, %s" % "default")

        # initialize queue
        for start_url in self.start_urls:
            self.active_queue.put(start_url)

        if self.debug:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

    def get_tld(self, url):
        """Get the top level domain given the url"""
        return urlsplit(url).netloc

    def crawl(self, max_urls=None):
        if max_urls:
            self.max_urls = max_urls

        try:
            while True:
                ips = self.urls_by_ips()

                # spawn child thread for urls per ip basis
                self.spawn_reader_threads(ips)

                # main thread more responsive than when calling thread.join for
                # spawned thread, wait for spawned threads to terminate after
                # each jump
                while threading.active_count() > 1:
                    time.sleep(0.1)

                # must visit the max_level so max_level + 1
                self.swap_queues()
                self.level += 1

                # check termination
                if self.level == (self.max_levels + 1):
                    logging.info("Reached jump level %s" % self.max_levels)
                    break

                if self.total_url_count == self.max_urls:
                    logging.info("Reached total read url count %s" %
                                 self.total_url_count)
                    break

        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def swap_queues(self):
        """Swap the full and empty queue.

        .. note::
            If the first url cannot be read for whatever reason, the program
            will swap through the queue multiple times util max levels is
            reached and stop. This can occur with the proxy spider if the
            proxy is not valid.
        """
        # logging.info("Swapping queues")
        (self.empty_queue, self.active_queue) = (self.active_queue,
                                                 self.empty_queue)

    def spawn_reader_threads(self, ips):
        """Spawn a thread associated with each ip"""
        try:
            # for py27 support
            ipitems = ips.iteritems()
        except AttributeError:
            ipitems = ips.items()

        for ((ip, root_url), urls) in ipitems:
            child_thread = threading.Thread(target=self.read,
                                            args=(ip, root_url, urls))
            child_thread.daemon = True
            child_thread.start()

    def urls_by_ips(self):
        """Group urls by host ip address"""
        ips = defaultdict(set)  # remove duplicates

        while not self.active_queue.empty():

            url = self.active_queue.get()

            if url.rstrip("/") in self.visited:
                logging.info("Already visited url, %s" % url)
                continue

            # test if external link and skip
            if self.follow_external_links is False:
                try:
                    if self.get_tld(url) not in self.tlds:
                        logging.info("Skipping external url, %s" % url)
                        continue
                except:
                    logging.warning("Invalid top level url, %s" % url)
                    continue

            # robots.txt for top level domain, note one ip can host multiple
            # sites
            robots = {}
            try:
                loc = self.get_tld(url)
                base_url = urlsplit(url).geturl()

                # create robotparser object
                try:
                    scheme = base_url.split(":")[0]
                    root_url = "".join([scheme, "://", loc])
                    robot = robots.setdefault(loc, root_url)
                except IOError:
                    robot = None
                    logging.warning("Unable to read robots.txt",
                                    "for url, %s" % base_url)

                # the split(':') allows for port numbers including
                # localhost:8080
                ips[(gethostbyname(loc.split(":")[0]),
                    robot)].add((base_url, url))

            except:
                logging.warning("Unable to group url, %s" % url)
                continue

        return ips

    def read(self, ip, root_url, urls):
        """One thread reads and parses urls from one server ip, i.e. one item
        from the queue. This allows for the thread to respect the server while
        going through the list sequentially. When proxies are used, each thread
        cycles through the proxies one by one when reading each url.

        ip - server ip addresss

        root_url - the top level url, something like, news.yahoo.com

        urls - tuple of (base_url, url) where base_url contains current path
        of the browser location if you will.

        The url is the absolute path to the html file that can can be directly
        passed in to be read by the backend.
        """
        if root_url and self.read_robots_file:
            try:
                rp = RobotFileParser(root_url)
                rp.read()
                logging.info("Reading robots.txt file for url %s" % root_url)
            except IOError:
                logging.warning("Unable to create robotparser, url skipped")

        for base_url, url in urls:
            try:
                # check robots file
                if rp.can_fetch("*", url) is False:
                    logging.info("robots.txt from %s rejected spider" % url)
                    continue
            except:
                logging.info("Ignoring robots.txt file")

            try:
                # download the raw html - note urls contains 'http' or 'https'
                html = self.backend.urlread(url, timeout=self.timeout)
                logging.info("Downloaded url, %s" % url)

                # note as visited - deques are threadsafe for append
                self.visited.append(url.rstrip("/"))

                if self.thread_safe_parse:
                    with self.lock:
                        follow_links = self.parse(url, html)
                else:
                    follow_links = self.parse(url, html)

                self.total_url_count += 1

            except:
                logging.warning("Unable to download and parse url, %s" % url)
                self.visited.append(url.rstrip("/"))

            # stop each thread if max count is reached
            if self.total_url_count == self.max_urls:
                break

            try:
                if follow_links is None:        # nothing is returned
                    # extract all new urls, when parse returns nothing
                    new_urls = self.backend.urlparse(html)
                elif follow_links is False:     # user initiated termination
                    new_urls = []
                else:
                    # user provided urls returned by self.parse
                    new_urls = follow_links


                # to limit the number of urls added by each thread the work is
                # reduced instead of trying to coordinate the threads somemhow
                qsize = self.max_urls_per_level     # queue size
                nthreads = threading.active_count() - 1     # not main thread
                urls_per_thread = qsize // nthreads

                if urls_per_thread > len(new_urls):
                    urls_per_thread = len(new_urls)

                for new_url in random.sample(new_urls, urls_per_thread):
                    try:
                        # print(urljoin(base_url, new_url))
                        self.empty_queue.put(urljoin(base_url, new_url),
                                             timeout=0.1)
                    except Full:
                        logging.info("Queue is full, skipping remaining urls")
                        break
            except AttributeError:
                logging.warning("Unable to extract urls from url, %s" % url)

            # wait to respect server before jumping expect if one url only
            if self.respect_server and len(urls) > 1:
                logging.info("Respecting server at, %s" % ip)
                try:
                    # python 3.6 method
                    delay = rp.crawl_delay("*")
                    self.wait(delay=delay)
                except (NameError, AttributeError):
                    self.wait()

    @abstractmethod
    def parse(self, url, html):
        """User code used to handle each url and corresponding html.

        By default the spider will crawl all urls in the html body in the next
        iteration or jump.

        The user can return a list of urls to follow which is added to the
        empty queue. Using this approach the spider can be directed to crawl to
        specific pages based on user defined logic and requirements, pagination
        for example. If parse returns False, all urls are ignored. Note, by
        default class methods implicitly return None if nothing else is.

        .. attention::
            The user defined urls in the list must all be absolute urls.

        Note, after the empty queue size limit is reached, any remaining urls

        in the list will not be added to the empty queue. In addition, external
        urls will not be followed unless the follow_external_links attribute is
        set to True.
        """
        raise NotImplementedError("implement")

    def wait(self, delay=None):
        """Enter the total delay time in seconds"""
        if delay is None:
            delay = random.randrange(*self.wait_time_range)
        time.sleep(delay)
