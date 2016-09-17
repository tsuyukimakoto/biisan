import biisan
import os
import codecs
from glob import glob
import logging
from multiprocessing import Pool
import xml.etree.ElementTree as ET

from docutils.core import publish_parts
from docutils.parsers.rst import directives
from glueplate import config

from biisan.utils import get_klass, get_function
from biisan.processors import FunctionRegistry

logging.basicConfig(level=config.settings.log_level)
logger = logging.getLogger(__name__)
processor_registry = None


def unmarshal_story(pth):
    story_class = get_klass(config.settings.story_class)
    with codecs.open(pth, encoding='utf8') as f:
        logger.debug('Unmarshal : {0}'.format(pth))
        data = f.read()
        parts = publish_parts(data, writer_name='xml')
        document = ET.fromstring(parts.get('whole'))
        _story = story_class()
        _story.rst_file = pth
        processor_registry.process(document, _story)
        return _story


def glob_rst_documents(base_path):
    pool = Pool(config.settings.multiprocess)
    story_list = pool.map(
        unmarshal_story,
        list(glob('{0}/**/*.rst'.format(base_path), recursive=True))
    )
    story_list.sort()
    # for story in story_list:
    #     print(story)
    return story_list


def write_html(story):
    os.makedirs(story.directory, exist_ok=True)
    with codecs.open(
        os.path.join(
            story.directory, 'index.html'), 'w', 'utf8') as f:
        f.write(story.to_html())


def output(story_list):
    # pool = Pool(config.settings.multiprocess)
    # pool.map(
    #     write_html,
    #     story_list
    # )
    for i, story in enumerate(story_list):
        story.prepare_html(story_list, i)
        write_html(story)


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


def print_fire_message():
    m = '''BIISAN {0}'''.format(biisan.__version__)
    print(m)

if __name__ == '__main__':
    print_fire_message()
    register_directives()
    register_processor()
    story_list = glob_rst_documents('.')
    # story_list = glob_rst_documents('./2013/05')
    output(story_list)
