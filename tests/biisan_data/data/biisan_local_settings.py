import os
from glueplate import Glue as _

settings = _(
    blog = _(
        title = 'blog for test',
        base_url = 'http://localhost:8000',
        language = 'ja',
    ),
    dir = _(
        output = os.path.abspath(os.path.join('..', 'out'))
    ),
    GLUE_PLATE_PLUS_BEFORE_template_dirs = [os.path.abspath(os.path.join('.', 'templates')),],
    multiprocess = 8,
)
