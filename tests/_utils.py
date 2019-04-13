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


