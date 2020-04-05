"""Publish to pypi.org using twine.

Run this from within the virtual environment.
"""

from __future__ import print_function

import subprocess
import shutil

import os

from arackpy import ROOT_DIR


def publish():
    """Publish to pypy.org"""

    cmds = ["python setup.py sdist bdist_wheel",
            "twine upload --repository-url https://pypi.org/legacy/ dist/*"]

    os.chdir(ROOT_DIR)

    if os.path.exists("dist"):
        shutil.rmtree("dist")

    if os.path.exists("build"):
        shutil.rmtree("build")

    try:
        for cmd in cmds:
            subprocess.call(cmd.split())
    except:
        print("Upload failed!")


if __name__ == "__main__":
    publish()
