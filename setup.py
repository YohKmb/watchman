# #! /usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import __init__

setup(
        name             = 'watchman',
        version          = __init__.__version__,
        description      = 'Graphical ICMP Monitoring Tool',
        license          = __init__.__license__,
        author           = __init__.__author__,
        author_email     = 'yoh134shonan@gmail.com',
        url              = 'https://github.com/YohKmb/watchman.git',
        keywords         = 'ping monitor gui tool',
        packages         = find_packages(),
        install_requires = ["Flask>=0.10.1"],
        )

