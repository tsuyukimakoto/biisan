from glueplate import Glue as _

settings = _(
    GLUE_PLATE_ENVIRONMENT_VARIABLE_KEY = 'BIISAN_SETTINGS_MODULE',
    entry_class = 'biisan.models.Entry',
    element_processors = [],
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
