from glueplate import Glue as _

settings = _(
    GLUE_PLATE_ENVIRONMENT_VARIABLE_KEY = 'BIISAN_SETTINGS_MODULE',
    entry_class = 'biisan.models.Entry',
    processors = [
        'biisan.processors.process_document',
        'biisan.processors.process_title',
        'biisan.processors.process_docinfo',
        'biisan.processors.process_field_name',
        'biisan.processors.process_field_body',
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
)
