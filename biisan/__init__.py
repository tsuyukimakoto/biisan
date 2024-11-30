import os
import multiprocessing

version_info = (0, 8, 2)
__version__ = ".".join([str(v) for v in version_info])

os.environ["GLUE_PLATE_BASE_MODULE"] = "biisan.biisan_settings"

multiprocessing.set_start_method("fork")
