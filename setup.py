#!/usr/bin/env python
'''
Physaliidae
============================================================

Static blog site generator.
'''
from distutils.core import setup

from biisan import __version__

setup(name='biisan',
      version=__version__,
      description='Static site generator.',
      author='makoto tsuyuki',
      author_email='mtsuyuki@gmail.com',
      url='https://github.com/tsuyukimakoto/biisan',
      scripts=['scripts/katsuebo'],
      long_description=__doc__,
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX',
                   'Operating System :: Unix',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Documentation',
                   ],
      packages=['biisan', 'biisan.directives', ],
      package_data={'biisan': ['templates/*', ]},
      )
