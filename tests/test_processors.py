import pytest

from biisan.main import initialize_structures
from ._constants import (
    ANSWER,
    DATA_DIR,
)
from ._utils import (
    cd,
    cleanup,
    setenv,
)


def test_register_processor():
    initialize_structures(DATA_DIR, ANSWER)

    # need data structure before import biisan.generate
    from biisan.generate import register_processor
    from glueplate import config

    register_processor()

    import biisan.generate
    assert biisan.generate.processor_registry is not None

    assert ['biisan.processors.' + processor for processor in list(
        biisan.generate.processor_registry.keys())
    ] == config.settings.processors
