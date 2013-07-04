#!/usr/bin/python

from setuptools import setup

setup(name="radlibs",
      version="0.0.1",
      description="self-recursive turing-complete madlibs implementation",
      author="Andrew Lorente",
      author_email="andrew.lorente@gmail.com",
      url="github.com/andrewlorente/radsnap",
      packages=['radlibs'],
      scripts=[],
      install_requires=[
          "parsimonious",

          "nose",
          'mock',
      ],
      )
