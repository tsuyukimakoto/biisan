import biisan
import os
import codecs
import hashlib
import time
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

from biisan.utils import get_klass, get_function, get_environment
from biisan.processors import FunctionRegistry
from biisan.markdown_processor import parse_markdown_to_xml

logging.basicConfig(level=config.settings.log_level)
logger = logging.getLogger(__name__)
processor_registry = None
_DOCUTILS_SILENT_STREAM = open(os.devnull, 'w')


def __latest_stories(story_list):
    cnt = config.settings.latest_list_count * -1 - 1
    return story_list[:cnt:-1]


def _docutils_settings_overrides():
    overrides = {
        'report_level': getattr(config.settings, 'docutils_report_level', 2),
        'halt_level': getattr(config.settings, 'docutils_halt_level', 6),
    }
    if getattr(config.settings, 'docutils_quiet_warnings', False):
        overrides['warning_stream'] = _DOCUTILS_SILENT_STREAM
    return overrides


def unmarshal_story(pth):
    """
    Parse and unmarshal a story file (RST or Markdown).

    Args:
        pth: Path to the story file (.rst or .md)

    Returns:
        Story object with parsed content
    """
    story_class = get_klass(config.settings.story_class)
    with codecs.open(pth, encoding='utf8') as f:
        logger.debug('Unmarshal : {0}'.format(pth))
        data = f.read()

        # Determine file type and parse accordingly
        if pth.endswith('.md'):
            # Parse Markdown to XML
            document = parse_markdown_to_xml(data)

        elif pth.endswith('.rst'):
            # Parse RST to XML using docutils
            parts = publish_parts(
                data,
                writer_name='xml',
                settings_overrides=_docutils_settings_overrides(),
            )
            document = ET.fromstring(parts.get('whole'))
        else:
            raise ValueError(f'Unsupported file format: {pth}. Only .rst and .md are supported.')

        _story = story_class()
        _story.source_file = pth
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


def glob_documents(base_path):
    """
    Find and parse all story documents (RST and Markdown).

    Args:
        base_path: Base directory to search for documents

    Returns:
        Sorted list of Story objects
    """
    pool = Pool(config.settings.multiprocess)

    # Collect both .rst and .md files
    rst_files = list(glob('{0}/**/*.rst'.format(base_path), recursive=True))
    md_files = list(glob('{0}/**/*.md'.format(base_path), recursive=True))
    all_files = rst_files + md_files

    story_list = pool.map(unmarshal_story, all_files)
    pool.close()
    pool.join()
    story_list.sort()
    return story_list


# Backward compatibility alias
glob_rst_documents = glob_documents


def _digest_cache_path(story):
    return os.path.join(story.directory, '.biisan.raw.sha256')


def _read_digest_cache(cache_path):
    if not os.path.exists(cache_path):
        return None
    try:
        with codecs.open(cache_path, 'r', 'utf8') as f:
            return f.read().strip()
    except OSError:
        return None


def _write_digest_cache(cache_path, digest):
    with codecs.open(cache_path, 'w', 'utf8') as f:
        f.write(digest)


def write_html(story):
    os.makedirs(story.directory, exist_ok=True)
    _file = os.path.join(story.directory, 'index.html')
    cache_path = _digest_cache_path(story)
    rendered = story.to_html()
    digest = hashlib.sha256(rendered.encode('utf8')).hexdigest()
    cached_digest = _read_digest_cache(cache_path)

    # Fast path: if rendered content hasn't changed, skip minification and write.
    if cached_digest == digest and os.path.exists(_file):
        return False

    _data = html_minify(rendered)
    _current = None
    if os.path.exists(_file):
        with codecs.open(_file, 'r', 'utf8') as f:
            _current = f.read()
    if _current == _data:
        if cached_digest != digest:
            _write_digest_cache(cache_path, digest)
        return False
    with codecs.open(_file, 'w', 'utf8') as f:
        f.write(_data)
        logger.info('Write:{0}'.format(_file))
    _write_digest_cache(cache_path, digest)
    return True


def output(story_list):
    total = len(story_list)
    if total == 0:
        return
    logger.info('Render start: %d stories', total)
    start = time.monotonic()
    written = 0
    for i, story in enumerate(story_list, start=1):
        story.prepare_html(story_list, i - 1)
        if write_html(story):
            written += 1
        if i == 1 or i % 50 == 0 or i == total:
            elapsed = time.monotonic() - start
            logger.info(
                'Render progress: %d/%d (written=%d, elapsed=%.1fs)',
                i, total, written, elapsed
            )
    logger.info(
        'Render done: %d/%d written in %.1fs',
        written, total, time.monotonic() - start
    )


def write_extra(extra):
    extra_page = unmarshal_story('./extra/{0}.rst'.format(extra))
    extra_page.extra = extra
    extra_page.extra_directory(extra)
    output([extra_page])
    return extra_page


def write_top(context):
    env = get_environment(config)
    top = env.get_template('index.html')
    with codecs.open(
        os.path.join(
            config.settings.dir.output, 'index.html'), 'w', 'utf8') as f:
        f.write(top.render(**context))


def write_blog_top(story_list):
    latest_story_list = __latest_stories(story_list)
    year_month = extract_year_month(story_list)
    env = get_environment(config)
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
    env = get_environment(config)
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
    now_rfc2822 = formatdate(float(datetime.now(tz=config.settings.timezone).strftime('%s')))
    cnt = config.settings.latest_list_count * -1 - 1
    latest_story_list = story_list[:cnt:-1]
    env = get_environment(config)
    rss20 = env.get_template('rss20.xml')
    rss = rss20.render(config=config,
                       story_list=latest_story_list,
                       now_rfc2822=now_rfc2822)
    feed_dir = os.path.join(config.settings.dir.output, 'api', 'feed')
    os.makedirs(feed_dir, exist_ok=True)
    with codecs.open(os.path.join(feed_dir, 'index.xml'), 'w', 'utf8') as f:
        f.write(rss)


def __classify_category(story_list):
    res = {}
    for story in story_list:
        if story.has_additional_meta("category"):
            category = story.category
            if category in res:
                res[category].append(story)
            else:
                res[category] = [story]
    return res


def write_category_rss20(category, story_list):
    now_rfc2822 = formatdate(float(datetime.now(tz=config.settings.timezone).strftime('%s')))
    cnt = config.settings.latest_list_count * -1 - 1
    latest_story_list = story_list[:cnt:-1]
    env = get_environment(config)
    rss20 = env.get_template('rss20.xml')
    rss = rss20.render(config=config,
                       story_list=latest_story_list,
                       now_rfc2822=now_rfc2822)
    feed_dir = os.path.join(config.settings.dir.output, 'api', 'feed', category)
    os.makedirs(feed_dir, exist_ok=True)
    with codecs.open(os.path.join(feed_dir, 'index.xml'), 'w', 'utf8') as f:
        f.write(rss)


def write_sitemaps(story_list):
    last_modified_iso_8601 = max(map(lambda x: x.date, story_list)).isoformat()
    env = get_environment(config)
    sitemaps = env.get_template('sitemaps.xml')
    sitemap = sitemaps.render(config=config,
                              story_list=story_list,
                              last_modified=last_modified_iso_8601)
    sitemap_dir = os.path.join(
        config.settings.dir.output, 'api', 'google_sitemaps')
    os.makedirs(sitemap_dir, exist_ok=True)
    with codecs.open(os.path.join(sitemap_dir, 'index.xml'), 'w', 'utf8') as f:
        f.write(sitemap)


def write_all_entry(story_list):
    last_modified_iso_8601 = max(map(lambda x: x.date, story_list)).isoformat()
    env = get_environment(config)
    all_entry = env.get_template('blog_all.html')
    all_entries = all_entry.render(config=config,
                                   story_list=story_list,
                                   last_modified=last_modified_iso_8601)
    all_entry_dir = os.path.join(
        config.settings.dir.output, 'blog', 'all')
    os.makedirs(all_entry_dir, exist_ok=True)
    with codecs.open(os.path.join(all_entry_dir, 'index.html'), 'w', 'utf8') as f:
        f.write(all_entries)


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
    logger.info('Collecting stories...')
    start = time.monotonic()
    story_list = glob_documents('./blog')
    if len(story_list) == 0:
        logger.error('NO ENTRY FOUND.')
        return
    logger.info('Collected %d stories in %.1fs', len(story_list), time.monotonic() - start)
    output(story_list)
    context = {}
    context['config'] = config
    context['story_list'] = story_list
    context['latest_story_list'] = __latest_stories(story_list)
    for extra in config.settings.extra:
        context[extra] = write_extra(extra)
    write_top(context)
    write_blog_top(story_list)
    write_blog_archive(story_list)
    write_rss20(story_list)
    story_by_category = __classify_category(story_list)
    for category, _story_list in story_by_category.items():
        write_category_rss20(category, _story_list)
    write_sitemaps(story_list)
    write_all_entry(story_list)


if __name__ == '__main__':
    print_fire_message()
    prepare()
    main()
