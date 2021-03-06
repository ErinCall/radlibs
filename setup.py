#!/usr/bin/python

from setuptools import setup

setup(name="radlibs",
      version="0.0.1",
      description="self-recursive turing-complete madlibs implementation",
      author="Andrew Lorente",
      author_email="andrew.lorente@gmail.com",
      url="http://www.radlibs.info",
      packages=[
          'radlibs',
          'radlibs.web',
          'radlibs.web.controllers',
          'radlibs.table',
          'radlibs.english',
      ],
      scripts=[],
      install_requires=[],
      )
