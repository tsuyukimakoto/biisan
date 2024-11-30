SETTINGS_TMPL = """import os
from glueplate import Glue as _

settings = _(
    blog = _(
        title = '{blog_title}',
        base_url = '{base_url}',
        language = '{language}',
    ),
    dir = _(
        output = os.path.abspath(os.path.join('..', 'out'))
    ),
    GLUE_PLATE_PLUS_BEFORE_template_dirs = [os.path.abspath(os.path.join('.', 'templates')),],
    multiprocess = {multicore},
)
"""

ABOUT_TMPL = """About {blog_title}
=========================================================

:slug: about
:date: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}

"""

QUESTIONS = [
    {
        "type": "input",
        "name": "blog_title",
        "message": "What's your blog title",
    },
    {
        "type": "input",
        "name": "base_url",
        "message": "input your blog base url. like https://www.tsuyukimakoto.com",
    },
    {
        "type": "input",
        "name": "language",
        "message": "input your blog language like ja",
    },
]

BIISAN_DATA_DIR = "biisan_data"
