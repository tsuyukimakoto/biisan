import os

version_info = (0, 8, 1)
__version__ = ".".join([str(v) for v in version_info])

os.environ['GLUE_PLATE_BASE_MODULE'] = 'biisan.biisan_settings'
