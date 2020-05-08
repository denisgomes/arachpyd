"""Run tests on the local pydoc server. Note, this is a simple hack for
integration testing.
"""

from __future__ import print_function

import atexit
import os
import signal
import subprocess
import time
import unittest

from arackpy import ROOT_DIR
from arackpy.spider import Spider


TEST_DIR = os.path.join(ROOT_DIR, "tests")

DOC_SERVER = None
DOC_SERVER_PORT = 10000

PROXY_SERVER = None
PROXY_SERVER_PORT = 20000


def setUpModule():
    global DOC_SERVER, PROXY_SERVER

    # start servers once
    if DOC_SERVER is None and PROXY_SERVER is None:
        cmd = "python -m pydoc -p %s" % DOC_SERVER_PORT
        DOC_SERVER = subprocess.Popen(cmd.split())

        cmd2 = "python %s %s" % (os.path.join(TEST_DIR, "proxyserver.py"),
                                 PROXY_SERVER_PORT)
        PROXY_SERVER = subprocess.Popen(cmd2.split())

        # let servers start
        time.sleep(3)

        atexit.register(shutdown_servers, DOC_SERVER, PROXY_SERVER)


def shutdown_servers(DOC_SERVER, PROXY_SERVER):
    import time

    DOC_SERVER.kill()
    PROXY_SERVER.kill()

    time.sleep(3)


class TestSpider(Spider):

    wait_time_range = (1, 2)

    start_urls = ["http://localhost:%s" % DOC_SERVER_PORT]

    thread_safe_parse = True

    def stop_crawl(self):
        """Keyboard interrupt"""
        if hasattr(signal, 'CTRL_C_EVENT'):
            # windows. Need CTRL_C_EVENT to raise the signal in the
            # whole process group
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
        else:
            # unix.
            pgid = os.getpgid(os.getpid())
            if pgid == 1:
                os.kill(os.getpid(), signal.SIGINT)
            else:
                os.killpg(os.getpgid(os.getpid()), signal.SIGINT)


class TestCaseSpider(unittest.TestCase):
    """Start the pydoc server for testing the crawler"""

    pass
