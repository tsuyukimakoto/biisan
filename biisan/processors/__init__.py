from datetime import datetime
import logging

from glueplate import config


from biisan.models import (
    Comment, Paragraph, Section, BulletList, ListItem, Target, Raw, Image, BlockQuote, Title,
    LiteralBlock, Figure, Caption, Table, Thead, Tbody, Tgroup, ColSpec, Row, Entry, EnumeratedList, Transition,
    Topic, SubstitutionDefinition, Note, DefinitionList, DefinitionListItem, Term, Definition,
    Strong, Emphasis, Reference, Literal
)

logger = logging.getLogger(__name__)


def _debug(elm):
    logger.debug('-' * 20)
    logger.debug('Tag: {0}'.format(elm.tag))
    logger.debug('text: {0}'.format(elm.text))
    logger.debug('------- items --------------')
    logger.debug(elm.items())
    logger.debug('------- getchildren --------')
    logger.debug(list(elm))
    logger.debug('-' * 20)


def _datetime_with_tz(time_str):
    _date = datetime.strptime(
        time_str, '%Y-%m-%d %H:%M'
    )
    _tm = _date.timetuple()
    return datetime(
        _tm.tm_year,
        _tm.tm_mon,
        _tm.tm_mday,
        _tm.tm_hour,
        _tm.tm_min,
        tzinfo=config.settings.timezone,
    )


def process_field_name(elm, registry, container):
    # print(f"[DEBUG] process_field_name: {elm.text}")
    return elm.text


def process_field_body(elm, registry, container):
    # print(f"[DEBUG] process_field_body: tag={elm.tag}, children={len(list(elm))}")
    res = []
    for x in list(elm):
        # print(f"[DEBUG]   child: tag={x.tag}, text={x.text}")
        if 'field_list' == x.tag:
            logger.warning("Ignore field_list in field_body's child")
        else:
            res.append(x.text)
    # print(f"[DEBUG] process_field_body result: {res}")
    return res


def process_list_item(elm, registry, container):
    list_item = ListItem()
    container.add_content(list_item)
    for _elm in list(elm):
        registry.process(_elm, list_item)


def process_bullet_list(elm, registry, container):
    bullet_list = BulletList()
    container.add_content(bullet_list)
    for _elm in list(elm):
        registry.process(_elm, bullet_list)


def process_definition_list(elm, registry, container):
    definition_list = DefinitionList()
    container.add_content(definition_list)
    for _elm in list(elm):
        registry.process(_elm, definition_list)


def process_definition(elm, registry, container):
    definition = Definition()
    container.definition = definition
    for _elm in list(elm):
        registry.process(_elm, definition)


def process_definition_list_item(elm, registry, container):
    definition_list_item = DefinitionListItem()
    container.add_content(definition_list_item)
    for _elm in list(elm):
        if _elm.tag == 'term':
            term = Term()
            term.text = _elm.text
            definition_list_item.term = term
        elif _elm.tag == 'definition':
            registry.process(_elm, definition_list_item)


def process_target(elm, registry, container):
    target = Target()
    container.add_content(target)
    for subitem in elm.items():
        if subitem[0] == 'ids':
            target.ids = subitem[1]
        elif subitem[0] == 'names':
            target.names = subitem[1]
        elif subitem[0] == 'uri' or subitem[0] == 'refuri':
            target.uri = subitem[1]


def process_reference(elm, registry, container):
    reference = Reference()
    # Use itertext() to get all text, or use elm.text attribute if available
    reference.text = elm.text if elm.text else ''.join(elm.itertext())
    container.add_content(reference)
    for subitem in elm.items():
        if subitem[0] == 'name':
            reference.name = subitem[1]
        elif subitem[0] == 'uri' or subitem[0] == 'refuri':
            reference.uri = subitem[1]


def process_raw(elm, registry, container):
    raw = Raw()
    container.add_content(raw)
    for subitem in elm.items():
        if subitem[0] == 'format':
            raw.format = subitem[1]
    raw.text = elm.text


def process_image(elm, registry, container):
    img = Image()
    container.add_content(img)
    for subitem in elm.items():
        if subitem[0] == 'alt':
            img.alt = subitem[1]
        elif subitem[0] == 'width':
            img.width = subitem[1]
        elif subitem[0] == 'height':
            img.height = subitem[1]
        elif subitem[0] == 'uri':
            img.uri = subitem[1]


def process_block_quote(elm, registry, container):
    block_quote = BlockQuote()
    container.add_content(block_quote)
    for _elm in list(elm):
        registry.process(_elm, block_quote)


def process_literal_block(elm, registry, container):
    literal_block = LiteralBlock()
    container.add_content(literal_block)
    literal_block.text = elm.text


def process_figure(elm, registry, container):
    figure = Figure()
    container.add_content(figure)
    for _elm in list(elm):
        registry.process(_elm, figure)


def process_topic(elm, registry, container):
    topic = Topic()
    container.add_content(topic)
    for _elm in list(elm):
        registry.process(_elm, topic)


def process_substitution_definition(elm, registry, container):
    substitution_definition = SubstitutionDefinition()
    container.add_content(substitution_definition)
    for _item in elm.items():
        if _item[0] == 'names':
            title = Title()
            title.text = _item[1]
            substitution_definition.title = title
    for _elm in list(elm):
        registry.process(_elm, substitution_definition)


def process_caption(elm, registry, container):
    caption = Caption()
    caption.text = elm.text
    container.add_content(caption)


def process_note(elm, registry, container):
    note = Note()
    container.add_content(note)
    for _elm in list(elm):
        registry.process(_elm, note)


def process_title(elm, registry, container):
    title = Title()
    title.text = elm.text
    container.title = title


def process_table(elm, registry, container):
    table = Table()
    container.add_content(table)
    for _elm in list(elm):
        registry.process(_elm, table)


def process_tgroup(elm, registry, container):
    tgroup = Tgroup()
    container.add_content(tgroup)
    for _elm in list(elm):
        registry.process(_elm, container)


def process_colspec(elm, registry, container):
    colspec = ColSpec()
    container.add_content(colspec)
    for item in elm.items():
        if hasattr(colspec, item[0]):
            setattr(colspec, item[1])


def process_thead(elm, registry, container):
    thead = Thead()
    container.add_content(thead)
    for _elm in list(elm):
        registry.process(_elm, thead)


def process_row(elm, registry, container):
    row = Row()
    if container.__class__ == Thead:
        row.header = True
    container.add_content(row)
    for _elm in list(elm):
        registry.process(_elm, row)


def process_entry(elm, registry, container):
    entry = Entry()
    container.add_content(entry)
    for _elm in list(elm):
        registry.process(_elm, entry)


def process_tbody(elm, registry, container):
    tbody = Tbody()
    container.add_content(tbody)
    for _elm in list(elm):
        registry.process(_elm, tbody)


# TODO test
def process_enumerated_list(elm, registry, container):
    enumerated_list = EnumeratedList()
    container.add_content(enumerated_list)
    for _elm in list(elm):
        registry.process(_elm, enumerated_list)


# TODO test
def process_transition(elm, registry, container):
    container.add_content(Transition())


def process_document(elm, registry, container):
    # print("[DEBUG] === process_document START ===")
    # print(f"[DEBUG] Document children count: {len(list(elm))}")
    for _elm in list(elm):
        # print(f"[DEBUG] Processing child: tag={_elm.tag}")
        registry.process(_elm, container)
    # print("[DEBUG] === process_document END ===")


def process_paragraph(elm, registry, container):
    paragraph = Paragraph()
    # Get all text for text-based element replacement
    paragraph.text = ''.join(elm.itertext())
    container.add_content(paragraph)
    # Process all child elements (including images)
    for _elm in list(elm):
        registry.process(_elm, paragraph)


def process_strong(elm, registry, container):
    strong = Strong()
    # Use itertext() to get all text including nested elements
    strong.text = ''.join(elm.itertext())
    container.add_content(strong)


def process_emphasis(elm, registry, container):
    emphasis = Emphasis()
    # Use itertext() to get all text including nested elements
    emphasis.text = ''.join(elm.itertext())
    container.add_content(emphasis)


def process_literal(elm, registry, container):
    literal = Literal()
    # Use itertext() to get all text
    literal.text = ''.join(elm.itertext())
    container.add_content(literal)


def process_section(elm, registry, container, depth=0):
    section = Section()
    container.add_content(section)
    # Check if XML element has depth attribute (from Markdown heading level)
    # Set this AFTER add_content to override automatic depth calculation
    if elm.get('depth'):
        # Set depth directly from Markdown heading level
        section.depth = int(elm.get('depth'))
    for _elm in list(elm):
        registry.process(_elm, section)


# TODO test
def _process_comment(elm, registry, story):
    _field_list = list(elm)[0]
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
            body += [x.text for x in _field[1]]
        elif 'create_date' == _field[0].text:
            create_date = _datetime_with_tz(_field[1][0].text)
        else:
            logger.warning(_field[0].text)
    c = Comment()
    c.commentator = commentator
    c.url = url
    for b in body:
        c.add_content(b)
    c.create_date = create_date
    story.comments.append(c)


def process_docinfo(elm, registry, story):
    # print("[DEBUG] === process_docinfo START ===")
    # print(f"[DEBUG] Number of children: {len(list(elm))}")

    for _elm in list(elm):
        # print(f"[DEBUG] Processing child element, length={len(_elm)}, tag={_elm.tag if hasattr(_elm, 'tag') else 'NO TAG'}")

        if len(_elm) == 2:
            # print(f"[DEBUG] Child[0] tag: {_elm[0].tag}, Child[1] tag: {_elm[1].tag}")

            if 'field_name' == _elm[0].tag:
                field_name = process_field_name(_elm[0], registry, story)
                # print(f"[DEBUG] >>> Processing field: {field_name}")

                if field_name == 'slug':
                    slug_value = process_field_body(_elm[1], registry, story)[0]
                    # print(f"[DEBUG] >>> Setting slug: {slug_value}")
                    story.slug = slug_value
                elif field_name == 'author':
                    author_value = process_field_body(_elm[1], registry, story)[0]
                    # print(f"[DEBUG] >>> Setting author: {author_value}")
                    story.author = author_value
                elif field_name == 'title':
                    # Support title field from YAML Front Matter
                    title_value = process_field_body(_elm[1], registry, story)[0]
                    # print(f"[DEBUG] >>> Setting title: {title_value}")
                    title = Title()
                    title.text = title_value
                    story.title = title
                elif field_name == 'date':
                    # Get date value from field_body
                    date_value = process_field_body(_elm[1], registry, story)[0]
                    # print(f"[DEBUG] >>> Setting date: {date_value} (type: {type(date_value)})")
                    if date_value:
                        story.date = _datetime_with_tz(date_value)
                        # print(f"[DEBUG] >>> Date set to: {story.date}")
                elif field_name == 'comment':
                    # print(f"[DEBUG] >>> Processing comment")
                    _process_comment(_elm[1], registry, story)
                else:
                    _value = process_field_body(
                        _elm[1], registry, story)[0]
                    # print(f"[DEBUG] >>> Setting additional_meta[{field_name}] = {_value}")
                    if _value is None:
                        logger.warning(
                            "docinfo needs escape : using \\ <- %s parse as None",
                            field_name,
                        )
                    story.additional_meta[field_name] = _value
            else:
                logger.warning(
                    "elm.tag '{0}' doesn't process in process_docinfo.".format(
                        _elm[0].tag))
        elif 'date' == _elm.tag:
            # print(f"[DEBUG] >>> Direct date element: {_elm.text}")
            story.date = _datetime_with_tz(_elm.text)
        elif 'author' == _elm.tag:
            # print(f"[DEBUG] >>> Direct author element: {_elm.text}")
            story.author = _elm.text

    # print("[DEBUG] === process_docinfo END ===")
    # print(f"[DEBUG] Final story.slug: {story.slug}")
    # print(f"[DEBUG] Final story.author: {story.author}")
    # print(f"[DEBUG] Final story.title: {story.title}")
    # Access private __date to avoid ValueError when None
    # print(f"[DEBUG] Final story._Story__date: {story._Story__date}")


class FunctionRegistry(dict):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if hasattr(value, '__call__'):
                self[key] = value
            else:
                raise ValueError('accept only callable.')

    def __setattr__(self, key, value):
        if hasattr(value, '__call__'):
            self[key] = value
            logger.debug(
                'register process function: {0}'.format(
                    self[key]))
        else:
            raise ValueError('accept only callable.')

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            object.__getattribute__(self, key)

    def register(self, name, func):
        setattr(self, name, func)

    def process(self, elm, container):
        _processor_name = 'process_{0}'.format(elm.tag)
        if hasattr(self, _processor_name):
            logger.debug('---------------')
            logger.debug(getattr(self, _processor_name).__name__)
            logger.debug(getattr(self, _processor_name).__code__.co_varnames)
            _fnc = getattr(self, _processor_name)
            return _fnc(elm, self, container)
        else:
            logger.debug(
                'processor {0} is not defined and element ignored.'.format(
                    _processor_name))
