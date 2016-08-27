import os
import codecs
from glob import glob
import xml.etree.ElementTree as ET
from docutils.core import publish_parts
import biisan.directives

version_info = (0, 1, 0)
__version__ = ".".join([str(v) for v in version_info])

x = None

os.environ['GLUE_PLATE_BASE_MODULE'] = 'biisan.biisan_settings'


def unmarshal_entry(pth):
    # TODO design Entry structure and factory
    with codecs.open(pth, encoding='utf8') as f:
        print(pth)
        data = f.read()
        parts = publish_parts(data, writer_name='xml')
        tree = ET.fromstring(parts.get('whole'))
        # TODO design element processor routine
    return tree


def glob_rst_documents(base_path):
    for pth in glob('**/*.rst', recursive=True):
        unmarshal_entry(pth)

if __name__ == '__main__':
    glob_rst_documents('.')
