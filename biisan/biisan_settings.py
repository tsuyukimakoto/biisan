from glueplate import Glue as _
import logging
import os


settings = _(
    GLUE_PLATE_ENVIRONMENT_VARIABLE_KEY = 'BIISAN_SETTINGS_MODULE',
    story_class = 'biisan.models.Story',
    latest_list_count = 5,
    processors = [
        'biisan.processors.process_document',
        'biisan.processors.process_title',
        'biisan.processors.process_docinfo',
        'biisan.processors.process_field_name',
        'biisan.processors.process_field_body',
        'biisan.processors.process_paragraph',
        'biisan.processors.process_section',
        'biisan.processors.process_bullet_list',
        'biisan.processors.process_list_item',
        'biisan.processors.process_target',
        'biisan.processors.process_raw',
        'biisan.processors.process_image',
        'biisan.processors.process_block_quote',
        'biisan.processors.process_literal_block',
        'biisan.processors.process_figure',
        'biisan.processors.process_caption',
        'biisan.processors.process_table',
        'biisan.processors.process_tgroup',
        'biisan.processors.process_colspec',
        'biisan.processors.process_thead',
        'biisan.processors.process_row',
        'biisan.processors.process_entry',
        'biisan.processors.process_tbody',
        'biisan.processors.process_enumerated_list',
        'biisan.processors.process_transition',
        'biisan.processors.process_topic',
        'biisan.processors.process_substitution_definition',
        'biisan.processors.process_note',
        'biisan.processors.process_definition_list',
        'biisan.processors.process_definition_list_item',
        'biisan.processors.process_definition',
        'biisan.processors.process_strong',
        'biisan.processors.process_emphasis',
        'biisan.processors.process_reference',
    ],
    directives = [
        'biisan.directives.PrismDirective',
        'biisan.directives.NotesDirective',
        'biisan.directives.AffDirective',
    ],
    directive = _(
        aff = _(
            tld='co.jp',
            tag='everes-22',
        ),
    ),
    extra = [
        'about',
    ],
    template_dirs = [os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates'),],
    multiprocess = 4,
    log_level = logging.INFO,
    dir = _(
        output = '/Users/makoto/Desktop/site'
    )
)
