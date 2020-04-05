from os.path import abspath, join, dirname

from arackpy.spider import Spider


__version__ = "0.2.0"
__release__ = "0.2.0a1"

ROOT_DIR = abspath(join(dirname(__file__), ".."))


__all__ = ["Spider"]
