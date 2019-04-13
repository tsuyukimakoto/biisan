from contextlib import contextmanager
from pathlib import Path
import os
import shutil

import pytest

@pytest.fixture(scope='function', autouse=True)
def cleanup():
    test_generate_dir = (Path('.') / 'tests' / 'biisan_data')
    if test_generate_dir.exists():
        shutil.rmtree(test_generate_dir)
    yield
    if test_generate_dir.exists():
        shutil.rmtree(test_generate_dir)


@pytest.fixture(scope='function', autouse=True)
def setenv():
    os.environ['BIISAN_SETTINGS_MODULE'] = 'tests.biisan_data.data.biisan_local_settings'
    yield
    del os.environ['BIISAN_SETTINGS_MODULE']


@contextmanager
def cd(to):
    prev_cwd = Path.cwd()
    os.chdir(to)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def _copy_blog(entry_file):
    src = Path('.') / 'test_data' / entry_file
    dest = Path('.') / 'biisan_data' / 'data' / 'blog' / entry_file
    shutil.copyfile(src, dest)


def copy_first_blog():
    _copy_blog('my_first_blog.rst')


def copy_second_blog():
    _copy_blog('my_second_blog.rst')


def copy_test_local_settings():
    src = Path('.') / 'test_data' / 'biisan_local_settings.py'
    dest = Path('.') / 'biisan_data' / 'data' / 'biisan_local_settings.py'
    shutil.copyfile(src, dest)
