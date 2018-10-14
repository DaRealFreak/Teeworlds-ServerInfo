#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

current_directory = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(current_directory, 'tw_serverinfo', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__description__'],
      url=about['__url__'],
      author=about['__author__'],
      author_email=about['__author_email__'],
      license=about['__license__'],
      packages=find_packages(),
      install_requires=[
          'pycountry>=18.5.26'
      ],
      extras_require={
      },
      zip_safe=True)
