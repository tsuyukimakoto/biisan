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
    copy_first_blog,
    copy_second_blog,
    copy_test_local_settings,
    setenv,
)


def test_register_processor():
    with cd('tests'):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()

        # need data structure before import biisan.generate
        from biisan.generate import register_processor
        from glueplate import config

        register_processor()

        import biisan.generate

        assert biisan.generate.processor_registry is not None
        assert ['biisan.processors.' + processor for processor in list(
            biisan.generate.processor_registry.keys())
        ] == config.settings.processors


def test_processors():
    with cd('tests'):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()
        copy_first_blog()
        copy_second_blog()

        with cd('biisan_data/data'):
            from biisan.generate import prepare, main

            prepare()
            main()
