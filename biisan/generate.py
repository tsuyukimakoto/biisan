import biisan
import codecs
from datetime import datetime
from glob import glob
import xml.etree.ElementTree as ET

from docutils.core import publish_parts
from docutils.parsers.rst import directives
from glueplate import config

from biisan.utils import get_klass


def process_field_name(elm):
    return elm.text


def process_field_body(elm, first=False):
    res = []
    for x in elm.getchildren():
        if first:
            return x.text
        res.append(x.text)
    if first:
        return None
    return res


def process_docinfo(elm):
    res = dict(slug='', author='', date=None)
    for _elm in elm.getchildren():
        if len(_elm) == 2:
            if 'field_name' == _elm[0].tag:
                field_name = process_field_name(_elm[0])
                if field_name in res.keys():
                    res[field_name] = process_field_body(_elm[1], first=True)
        elif 'date' == _elm.tag:
            res['date'] = datetime.strptime(
                _elm.text, '%Y-%m-%d %H:%M'
            )
    return res['slug'], res['author'], res['date']


def unmarshal_entry(pth):
    # TODO design Entry structure and factory
    entry_class = get_klass(config.settings.entry_class)
    with codecs.open(pth, encoding='utf8') as f:
        data = f.read()
        parts = publish_parts(data, writer_name='xml')
        document = ET.fromstring(parts.get('whole'))
        docinfo = document.find('docinfo')
        _title = document.find('title').text
        _slug, _author, _date = process_docinfo(docinfo)
        _entry = entry_class(slug=_slug, title=_title, author=_author,
                             date=_date)
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
        print(directive_class)

if __name__ == '__main__':
    '''
    '''
    register_directives()
    glob_rst_documents('.')
