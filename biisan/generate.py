import biisan
import codecs
from glob import glob
import logging
import xml.etree.ElementTree as ET

from docutils.core import publish_parts
from docutils.parsers.rst import directives
from glueplate import config

from biisan.utils import get_klass, get_function
from biisan.processors import FunctionRegistry

logger = logging.getLogger(__name__)
processor_registry = None


def unmarshal_entry(pth):
    entry_class = get_klass(config.settings.entry_class)
    with codecs.open(pth, encoding='utf8') as f:
        data = f.read()
        parts = publish_parts(data, writer_name='xml')
        document = ET.fromstring(parts.get('whole'))
        _entry = entry_class()
        processor_registry.process(document, _entry)
        return _entry


def glob_rst_documents(base_path):
    entry_list = []
    for pth in glob('**/*.rst', recursive=True):
        entry_list.append(unmarshal_entry(pth))
    entry_list.sort()
    for entry in entry_list:
        print(entry)


def register_directives():
    for directive in config.settings.directives:
        directive_class = get_klass(directive)
        directives.register_directive(
            directive_class.directive_tag,
            directive_class
        )
        logger.debug(directive_class)


def register_processor():
    global processor_registry
    processor_registry = FunctionRegistry()
    for processor in config.settings.processors:
        func = get_function(processor)
        processor_registry.register(func.__name__, func)


if __name__ == '__main__':
    register_directives()
    register_processor()
    glob_rst_documents('.')
