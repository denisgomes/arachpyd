"""Upload to test.pypi.org using twine.

Run this script from within the virtual environment.
"""

import subprocess
from datetime import datetime
import shutil

import os

from arackpy import ROOT_DIR


def get_setup_files():
    setup = open(os.path.join(ROOT_DIR, "setup.py")).readlines()

    new_setup = []
    for line in setup:
        timestamp = datetime.now().strftime('"%y.%m.%d.%H.%M.%S"')

        if line.strip().startswith("version"):
            line = "".join([line.split("=")[0], "=", timestamp, ",",
                            os.linesep])

        new_setup.append(line)

    return setup, new_setup


def upload():
    """Upload to test.pypy.org"""

    setup, new_setup = get_setup_files()

    cmds = ["python setup.py sdist bdist_wheel",
            "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"]

    os.chdir(ROOT_DIR)

    if os.path.exists("dist"):
        shutil.rmtree("dist")

    with open("setup.py", "w") as fp:
        fp.writelines(new_setup)

    try:
        for cmd in cmds:
            subprocess.call(cmd.split())
    except:
        print "Upload failed!"
    finally:
        with open("setup.py", "w") as fp:
            fp.writelines(setup)


if __name__ == "__main__":
    upload()
