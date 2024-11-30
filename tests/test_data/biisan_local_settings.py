import os

from glueplate import Glue as _

settings = _(
    blog=_(
        title="this is test title",
        base_url="http://localhost",
        language="ja",
    ),
    dir=_(output=os.path.abspath(os.path.join("biisan_data", "out"))),
    directive=_(
        appleaff=_(
            at="1000l898",
        ),
    ),
    GLUE_PLATE_PLUS_BEFORE_template_dirs=[
        os.path.abspath(os.path.join(".", "templates")),
    ],
    multiprocess=4,
)
