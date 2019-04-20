import biisan
import os
import codecs
from collections import OrderedDict
from glob import glob
import logging
from multiprocessing import Pool
from email.utils import formatdate
from datetime import datetime
import xml.etree.ElementTree as ET

from css_html_js_minify import html_minify
from docutils.core import publish_parts
from docutils.parsers.rst import directives
from glueplate import config
from jinja2 import Environment, FileSystemLoader

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


def extract_year_month(story_list):
    result = OrderedDict()
    for story in story_list:
        _months = result.get(story.date.year, [])
        _months.append(story.date.month)
        result[story.date.year] = _months
    for key in result.keys():
        result[key] = sorted(list(set(result.get(key))))
    return result


def pack_story_to_year_month(story_list):
    result = OrderedDict()
    for story in story_list:
        _year_month = '{0:04d}/{1:02d}'.format(
            story.date.year, story.date.month)
        _stories = result.get(_year_month, [])
        _stories.append(story)
        result[_year_month] = _stories
    return result


def glob_rst_documents(base_path):
    pool = Pool(config.settings.multiprocess)
    story_list = pool.map(
        unmarshal_story,
        list(glob('{0}/**/*.rst'.format(base_path), recursive=True))
    )
    story_list.sort()
    return story_list


def write_html(story):
    os.makedirs(story.directory, exist_ok=True)
    _file = os.path.join(story.directory, 'index.html')
    _data = html_minify(story.to_html())
    _current = None
    if os.path.exists(_file):
        with codecs.open(_file, 'r', 'utf8') as f:
            _current = f.read()
    if _current == _data:
        return
    with codecs.open(_file, 'w', 'utf8') as f:
        f.write(_data)
        logger.info('Write:{0}'.format(_file))


def output(story_list):
    for i, story in enumerate(story_list):
        story.prepare_html(story_list, i)
        write_html(story)


def write_extra(extra):
    extra_page = unmarshal_story('./extra/{0}.rst'.format(extra))
    extra_page.extra = extra
    extra_page.extra_directory(extra)
    output([extra_page])
    return extra_page


def write_top(context):
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    top = env.get_template('index.html')
    with codecs.open(
        os.path.join(
            config.settings.dir.output, 'index.html'), 'w', 'utf8') as f:
        f.write(top.render(**context))


def write_blog_top(story_list):
    cnt = config.settings.latest_list_count * -1 - 1
    latest_story_list = story_list[:cnt:-1]
    year_month = extract_year_month(story_list)
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    blog_top = env.get_template('blog_top.html')
    with codecs.open(
        os.path.join(
            config.settings.dir.output, 'blog', 'index.html'),
            'w', 'utf8') as f:
        f.write(blog_top.render(config=config,
                latest_story_list=latest_story_list,
                story_list=story_list, year_month=year_month))


def write_blog_archive(story_list):
    packed = pack_story_to_year_month(story_list)
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    blog_archive = env.get_template('blog_archive.html')
    for _year_month, stories in packed.items():
        with codecs.open(
            os.path.join(
                config.settings.dir.output, 'blog', _year_month,
                'index.html'),
                'w', 'utf8') as f:
            f.write(blog_archive.render(config=config,
                    year_month=_year_month, story_list=stories))


def write_rss20(story_list):
    now_rfc2822 = formatdate(float(datetime.now().strftime('%s')))
    cnt = config.settings.latest_list_count * -1 - 1
    latest_story_list = story_list[:cnt:-1]
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    rss20 = env.get_template('rss20.xml')
    rss = rss20.render(config=config,
                       story_list=latest_story_list,
                       now_rfc2822=now_rfc2822)
    feed_dir = os.path.join(config.settings.dir.output, 'api', 'feed')
    os.makedirs(feed_dir, exist_ok=True)
    with codecs.open(os.path.join(feed_dir, 'index.xml'), 'w', 'utf8') as f:
        f.write(rss)


def write_sitemaps(story_list):
    last_modified_iso_8601 = max(map(lambda x: x.date, story_list)).isoformat()
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    sitemaps = env.get_template('sitemaps.xml')
    sitemap = sitemaps.render(config=config,
                              story_list=story_list,
                              last_modified=last_modified_iso_8601)
    sitemap_dir = os.path.join(
        config.settings.dir.output, 'api', 'google_sitemaps')
    os.makedirs(sitemap_dir, exist_ok=True)
    with codecs.open(os.path.join(sitemap_dir, 'index.xml'), 'w', 'utf8') as f:
        f.write(sitemap)


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


def prepare():
    register_directives()
    register_processor()


def main():
    story_list = glob_rst_documents('./blog')
    if len(story_list) == 0:
        logger.error('NO ENTRY FOUND.')
        return
    output(story_list)
    context = {}
    context['config'] = config
    context['story_list'] = story_list
    for extra in config.settings.extra:
        context[extra] = write_extra(extra)
    write_top(context)
    write_blog_top(story_list)
    write_blog_archive(story_list)
    write_rss20(story_list)
    write_sitemaps(story_list)


if __name__ == '__main__':
    print_fire_message()
    prepare()
    main()
