import os
from email.utils import formatdate
import logging
from hashlib import md5

from glueplate import config

from biisan.utils import get_environment


logger = logging.getLogger(__name__)


class Container(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__body = []

    def __append_to_body(self, content):
        pass

    def add_content(self, content):
        # if issubclass(content.__class__, Document):
        #     content.cnt = len(self.__body) + 1
        if issubclass(self.__class__, Nestable) and (type(self) == type(content)):
            content.depth = self.depth + 1
        self.__append_to_body(content)
        self.__body.append(content)

    @property
    def contents(self):
        return self.__body


class Nestable(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = kwargs.get('depth', 1)


class HTMLize(object):
    env = get_environment(config)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_html(self):
        tmpl = HTMLize.env.get_template(
            os.path.join(
                'components',
                '{0}.html'.format(self.__class__.__name__).lower()
            )
        )
        return tmpl.render(element=self, config=config, hash_func=md5)


class Story(Container, HTMLize):
    def __init__(self):
        super().__init__()
        self.slug = ''
        self.title = ''
        self.__date = None
        self.author = ''
        self.__body = []
        self.comments = []
        self._timestamp = None
        self.source_file = ''
        self.extra = None
        self.additional_meta = {}

    def __lt__(self, other):
        try:
            return self._timestamp <= other._timestamp
        except TypeError as e:
            logger.error('-' * 20)
            logger.error(self.source_file)
            logger.error(self.slug)
            logger.error(self.__body)
            logger.error('=' * 20)
            raise e

    def __repr__(self):
        return '{0}: {1} at {2}, {3} comments'.format(
            self.slug, self.title, self.__date, len(self.comments))

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, 'additional_meta')[name]
        except KeyError:
            object.__getattribute__(self, name)

    def has_additional_meta(self, name):
        return hasattr(self, name)

    @property
    def date(self):
        if self.__date is None:
            raise ValueError('date must not be None.')
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date
        self._timestamp = self.__date.timestamp()

    @property
    def directory(self):
        if not hasattr(self, '_directory'):
            self._directory = os.path.join(
                '{0}'.format(config.settings.dir.output),
                'blog',
                '{0:04d}'.format(self.__date.year),
                '{0:02d}'.format(self.__date.month),
                '{0:02d}'.format(self.__date.day),
                self.slug
            )
        return self._directory

    @property
    def archive_directory(self):
        return os.path.join(
            '{0}'.format(config.settings.dir.output),
            'archive',
            '{0:04d}'.format(self.__date.year),
            '{0}'.format(self.__date.month)
        )

    @property
    def url(self):
        return '/blog/{0:04d}/{1:02d}/{2:02d}/{3}/{4}'.format(
            self.__date.year,
            self.__date.month,
            self.__date.day,
            self.slug,
            '')

    @property
    def publishd_date(self):
        return '{0:04d}-{1:02d}-{2:02d}/'.format(
            self.__date.year,
            self.__date.month,
            self.__date.day)

    @property
    def published_datetime(self):
        return '{0:04d}/{1:02d}/{2:02d} {3:02d}:{4:02d}'.format(
            self.__date.year,
            self.__date.month,
            self.__date.day,
            self.__date.hour,
            self.__date.minute)

    @property
    def publish_date_rfc2822(self):
        return formatdate(float(self.__date.strftime('%s')))

    @property
    def publish_datetime_iso_8601(self):
        return self.__date.isoformat()

    def prepare_html(self, story_list, i):
        self.prev_story = previous_story(story_list, i)
        self.next_story = next_story(story_list, i)

    def extra_directory(self, directory):
        self._directory = os.path.join(
            '{0}'.format(config.settings.dir.output),
            directory)


def archive_directory(year_month):
    return os.path.join(
        '{0}'.format(config.settings.dir.output),
        'archive', year_month)


class Comment(Container):
    def __init__(self):
        super().__init__()
        self.commentator = ''
        self.url = ''
        self.create_date = None

    # def add_content(self, content):
    #     self.__body.append(content)

    # @property
    # def contents(self):
    #     return self.__body

    @property
    def comemnted_datetime(self):
        return '{0:04d}/{1:02d}/{2:02d} {3:02d}:{4:02d}'.format(
            self.create_date.year,
            self.create_date.month,
            self.create_date.day,
            self.create_date.hour,
            self.create_date.minute)


def next_story(story_list, i):
    if i >= len(story_list) - 1:
        return '', ''
    target = story_list[i + 1]
    return target.title, target.url


def previous_story(story_list, i):
    if i == 0:
        return '', ''
    target = story_list[i - 1]
    return target.title, target.url


class Document():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnt = 0


class Paragraph(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''

    @property
    def formated(self):
        # For inline elements that need text replacement
        _formated = self.text

        # First pass: replace text-based inline elements
        for content in self.contents:
            if isinstance(content, Strong):
                _formated = _formated.replace(
                    content.text, '<strong>{0}</strong>'.format(
                        content.text))
            elif isinstance(content, Emphasis):
                _formated = _formated.replace(
                    content.text, '<i>{0}</i>'.format(
                        content.text))
            elif isinstance(content, Literal):
                _formated = _formated.replace(
                    content.text, '<code>{0}</code>'.format(
                        content.text))
            elif isinstance(content, Reference):
                _name = content.name and content.name or content.text
                if content.text:  # Only replace if text exists
                    _formated = _formated.replace(
                        content.text,
                        '<a href="{0}">{1}</a>'.format(
                            content.uri, _name))
            elif isinstance(content, Raw):
                _formated = _formated.replace(
                    content.text,
                    '<pre class="code {0}">{1}</pre>'.format(
                        content.format, content.text))

        # Second pass: append non-text elements (like images)
        for content in self.contents:
            if isinstance(content, Image):
                # Image doesn't have text to replace, so we append it
                _formated += content.to_html()
            elif not isinstance(content, (Strong, Emphasis, Literal, Reference, Raw)):
                logger.warning(
                    "Type:{0} in paragraph doesn't treat.".format(
                        type(content)))

        return _formated


class Strong(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''


class Emphasis(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''


class Section(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = ''


class BulletList(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EnumeratedList(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ListItem(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Title(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''

    def __repr__(self):
        return self.text or ''


class Target(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.ids = ''
        self.names = ''
        self.uri = ''


class Reference(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.uri = ''
        self.text = ''


class Literal(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.text = ''


class Raw(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.format = ''
        self.text = ''


class Image(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.alt = ''
        self.uri = ''
        self._width = None
        self._height = None

    @property
    def width(self):
        if not self._width:
            return ''
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if not self._height:
            return ''
        return self._height

    @height.setter
    def height(self, value):
        self._height = value


class BlockQuote(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LiteralBlock(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = kwargs.get('text', '')


class Figure(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Caption(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''


class Table(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Title()


class Thead(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tbody(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tgroup(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ColSpec(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colname = ''
        self.width = None
        self.scale = 100


class Row(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = False

    def to_html(self):
        if not self.header:
            return super().to_html()
        tmpl = HTMLize.env.get_template(
            os.path.join(
                'components',
                'header_{0}.html'.format(self.__class__.__name__).lower()
            )
        )
        return tmpl.render(element=self, config=config, hash_func=md5)


class Entry(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Transition(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Topic(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Title()


class SubstitutionDefinition(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Title()


class Note(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DefinitionList(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Term(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = kwargs.get('text', '')


class Definition(Document, Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DefinitionListItem(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.term = Term()
        self.definition = Definition()
