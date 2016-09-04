# import types
from datetime import datetime
import logging

from biisan.models import (
    Comment, Paragraph, Section, BulletList, ListItem, Target, Raw, Image, BlockQuote, Title,
    LiteralBlock, Figure, Caption, Table, ColSpec, Row, Entry, EnumeratedList, Transition,
    Topic, SubstitutionDefinition
)

logger = logging.getLogger(__name__)


def _debug(elm):
    print('-' * 20)
    print('Tag: {0}'.format(elm.tag))
    print('text: {0}'.format(elm.text))
    print('------- items --------------')
    print(elm.items())
    print('------- getchildren --------')
    print(elm.getchildren())
    print('-' * 20)


def process_field_name(elm, registry, container):
    return elm.text


def process_field_body(elm, registry, container):
    res = []
    for x in elm.getchildren():
        if 'field_list' == x.tag:
            logger.warn("Ignore field_list in field_body's child")
        else:
            res.append(x.text)
    return res


def process_list_item(elm, registry, container):
    list_item = ListItem()
    container.add_content(list_item)
    for _elm in elm.getchildren():
        registry.process(_elm, list_item)


def process_bullet_list(elm, registry, container):
    bullet_list = BulletList()
    container.add_content(bullet_list)
    for _elm in elm.getchildren():
        registry.process(_elm, bullet_list)


def process_target(elm, registry, container):
    target = Target()
    container.add_content(Target())
    for subitem in elm.items():
        if subitem[0] == 'ids':
            target.ids = subitem[1]
        elif subitem[0] == 'names':
            target.names = subitem[1]
        elif subitem[0] == 'uri':
            target.uri = subitem[1]


def process_raw(elm, registry, container):
    raw = Raw()
    container.add_content(raw)
    for subitem in elm.items():
        if subitem[0] == 'format':
            raw.format = subitem[1]


def process_image(elm, registry, container):
    img = Image()
    container.add_content(img)
    for subitem in elm.items():
        if subitem[0] == 'alt':
            img.alt = subitem[1]
        elif subitem[0] == 'witdh':
            img.witdh = subitem[1]
        elif subitem[1] == 'height':
            img.height = subitem[1]
        elif subitem[0] == 'uri':
            img.uri = subitem[1]


def process_block_quote(elm, registry, container):
    block_quote = BlockQuote()
    container.add_content(block_quote)
    for _elm in elm.getchildren():
        registry.process(_elm, block_quote)


def process_literal_block(elm, registry, container):
    literal_block = LiteralBlock()
    container.add_content(literal_block)
    literal_block.text = elm.text


def process_figure(elm, registry, container):
    figure = Figure()
    container.add_content(figure)
    for _elm in elm.getchildren():
        registry.process(_elm, figure)


def process_topic(elm, registry, container):
    topic = Topic()
    container.add_content(topic)
    for _elm in elm.getchildren():
        registry.process(_elm, topic)


def process_substitution_definition(elm, registry, container):
    substitution_definition = SubstitutionDefinition()
    container.add_content(substitution_definition)
    for _item in elm.items():
        if _item[0] == 'names':
            title = Title()
            title.text = _item[1]
            substitution_definition.title = title
    for _elm in elm.getchildren():
        registry.process(_elm, substitution_definition)


def process_caption(elm, registry, container):
    caption = Caption()
    caption.text = elm.text
    container.add_content(caption)


def process_title(elm, registry, container):
    title = Title()
    title.text = elm.text
    container.title = title


def process_table(elm, registry, container):
    table = Table()
    for _elm in elm.getchildren():
        registry.process(_elm, table)


def process_tgroup(elm, registry, container):
    for _elm in elm.getchildren():
        registry.process(_elm, container)


def process_colspec(elm, registry, container):
    colspec = ColSpec()
    for item in elm.items():
        if hasattr(colspec, item[0]):
            setattr(colspec, item[1])


def process_thead(elm, registry, container):
    for _elm in elm.getchildren():
        registry.process(_elm, container)


def process_row(elm, registry, container):
    row = Row()
    container.add_content(row)
    for _elm in elm.getchildren():
        registry.process(_elm, row)


def process_entry(elm, registry, container):
    entry = Entry()
    container.add_content(entry)
    for _elm in elm.getchildren():
        registry.process(_elm, entry)


def process_tbody(elm, registry, container):
    for _elm in elm.getchildren():
        registry.process(_elm, container)


def process_enumerated_list(elm, registry, container):
    enumerated_list = EnumeratedList()
    container.add_content(enumerated_list)
    for _elm in elm.getchildren():
        registry.process(_elm, enumerated_list)


def process_transition(elm, registry, container):
    container.add_content(Transition())


def process_document(elm, registry, container):
    for _elm in elm.getchildren():
        registry.process(_elm, container)


def process_paragraph(elm, registry, container):
    paragraph = Paragraph()
    paragraph.text = elm.text
    container.add_content(paragraph)


def process_section(elm, registry, container, depth=0):
    section = Section()
    container.add_content(section)
    for _elm in elm.getchildren():
        registry.process(_elm, section)


def _process_comment(elm, registry, story):
    _field_list = elm.getchildren()[0]
    commentator = ''
    url = ''
    body = []
    create_date = None
    for _field in _field_list:
        if 'commentator' == _field[0].text:
            commentator = _field[1][0].text
        elif 'url' == _field[0].text:
            url = _field[1].text
        elif 'body' == _field[0].text:
            body = [x.text for x in _field[1]]
        elif 'create_date' == _field[0].text:
            create_date = datetime.strptime(
                _field[1][0].text, '%Y-%m-%d %H:%M'
            )
    c = Comment()
    c.commentator = commentator
    c.url = url
    map(c.add_content, body)
    c.create_date = create_date
    story.comments.append(c)


def process_docinfo(elm, registry, story):
    for _elm in elm.getchildren():
        if len(_elm) == 2:
            if 'field_name' == _elm[0].tag:
                field_name = process_field_name(_elm[0], registry, story)
                if field_name == 'slug':
                    story.slug = process_field_body(
                        _elm[1], registry, story)[0]
                elif field_name == 'author':
                    story.author = process_field_body(
                        _elm[1], registry, story)[0]
                elif field_name == 'date':
                    story.date = datetime.strptime(
                        _elm.text, '%Y-%m-%d %H:%M'
                    )
                elif field_name == 'comment':
                    _process_comment(_elm[1], registry, story)
            else:
                logger.warn(
                    "elm.tag '{0}' doesn't process in process_docinfo.".format(
                        _elm[0].tag))
        elif 'date' == _elm.tag:
            story.date = datetime.strptime(
                _elm.text, '%Y-%m-%d %H:%M'
            )
            if story.rst_file == '2009/10/01280.rst':
                print(_elm.text)
                print(story.date)
        elif 'author' == _elm.tag:
            story.author = _elm.text


class FunctionRegistry(dict):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if hasattr(value, '__call__'):
                # self[key] = types.MethodType(value, self)
                self[key] = value
            else:
                raise ValueError('accept only callable.')

    def __setattr__(self, key, value):
        if hasattr(value, '__call__'):
            # self[key] = types.MethodType(value, self)
            self[key] = value
            logger.debug(
                'register process function: {0}'.format(
                    self[key]))
        else:
            raise ValueError('accept only callable.')

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            object.__getattribute__(self, key)

    def register(self, name, func):
        setattr(self, name, func)

    def process(self, elm, container):
        _processor_name = 'process_{0}'.format(elm.tag)
        if hasattr(self, _processor_name):
            logger.debug('---------------')
            logger.debug(getattr(self, _processor_name).__name__)
            logger.debug(getattr(self, _processor_name).__code__.co_varnames)
            return getattr(self, _processor_name)(elm, self, container)
        else:
            logger.warn(
                'processor {0} is not defined and element ignored.'.format(
                    _processor_name))
