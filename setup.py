from setuptools import setup, find_packages

from arackpy import __release__


long_description = open("README", "r").read()


setup(

    name="arackpy",

    version=__release__,

    description="A simple multithreaded web crawler and scraper.",

    # display on pypi
    long_description=long_description,

    url="https://www.github.com/denisgomes/arackpy",

    author="Denis Gomes",

    author_email="denis.mp.gomes@gmail.com",

    license="BSD",

    # advertise program attributes
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        ],

    keywords="web crawler scraper spider",

    # excluded in build distributions, applies to packages only
    packages=find_packages(exclude=[
        "arackpy.docs", "arackpy.examples", "arackpy.tests"
        ]),

    # install from pypi, requirements.txt is for developers only
    install_requires=[],

    package_data={},

    # MANIFEST.in works for source distributions only
    data_files=[("", ["LICENSE.txt", "README"])],

    # scripts= ,

    # tests
    test_suite="tests",

    )
