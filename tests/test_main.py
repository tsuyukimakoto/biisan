from pathlib import Path

import pytest

from biisan.main import (
    initialize_structures,
)

from ._constants import (
    ANSWER,
    DATA_DIR,
)
from ._utils import (  # noqa
    cd,
    cleanup,
)


def test_initialize_structures():
    with cd('tests'):
        initialize_structures(DATA_DIR, ANSWER)
        generated_biisan_data_dir = Path('.') / 'biisan_data'
        # assert generated directory
        assert (generated_biisan_data_dir / 'data' / 'blog').exists()
        assert (generated_biisan_data_dir / 'data' / 'templates').exists()
        assert (generated_biisan_data_dir / 'out').exists()
        # assert generated files
        assert (generated_biisan_data_dir / 'data' / 'biisan_local_settings.py').exists()
        assert (generated_biisan_data_dir / 'data' / 'extra' / 'about.rst').exists()


def test_initialize_structures_twice():
    with cd('tests'):
        initialize_structures(DATA_DIR, ANSWER)

        with pytest.raises(SystemExit):
            initialize_structures(DATA_DIR, ANSWER)
