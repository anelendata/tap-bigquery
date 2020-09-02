#!/usr/bin/env python
from setuptools import setup

VERSION = "0.3.1"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tap-bigquery",
    version=VERSION,
    description="Singer.io tap for extracting data from BigQuery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/tap_bigquery",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],

    install_requires=[
        "attrs==19.3.0",
        "backoff==1.8.0",
        "google-cloud-bigquery==1.16.0",
        "requests>=2.20.0",
        "simplejson==3.11.1",
        "singer-python>=5.2.0",
        "setuptools>=40.3.0",
    ],

    entry_points="""
    [console_scripts]
    tap-bigquery=tap_bigquery:main
    """,

    packages=["tap_bigquery"],
    package_data={
    },
    include_package_data=True,
)
