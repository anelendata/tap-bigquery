#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap_bigquery",
    version="0.2.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_bigquery"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests",
        "google-cloud-bigquery==1.16.0",
        "attrs==19.3.0"
    ],
    entry_points="""
    [console_scripts]
    tap_bigquery=tap_bigquery:main
    """,
    packages=["tap_bigquery"],
    package_data = {
        "schemas": ["tap_bigquery/schemas/*.json"]
    },
    include_package_data=True,
)
