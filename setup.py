#!/usr/bin/env python
'''
Biisan
============================================================

Static blog site generator.
'''
from setuptools import setup

from biisan import __version__

requirements = []
with open('requirements/requirements.txt', 'r') as f:
    requirements = [req.strip() for req in f.readlines() if req]

with open('README.md') as f:
    long_description = f.read()

setup(
    name='biisan',
    version=__version__,
    description='Static site generator.',
    keywords='static site generator, docutils, customizable',
    author='makoto tsuyuki',
    author_email='mtsuyuki@gmail.com',
    url='https://github.com/tsuyukimakoto/biisan',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Documentation',
    ],
    zip_safe=False,
    install_requires=requirements,
    packages=['biisan', 'biisan.directives', 'biisan.processors'],
    package_data={
          'biisan': ['templates/*', 'templates/components/*', ],
    },
)
