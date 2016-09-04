import os
from email.utils import formatdate

from glueplate import config


class Container(object):
    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self.__body = []

    def __append_to_body(self, content):
        pass

    def add_content(self, content):
        self.__append_to_body(content)
        self.__body.append(content)

    @property
    def contents(self):
        return self.__body


class Nestable(object):
    def __init__(self, *args, **kwargs):
        super(Nestable, self).__init__(*args, **kwargs)
        self.depth = kwargs.get('depth', 0)

    def __append_to_body(self, content):
        if type(content) == self.__class__:
            content.depth = self.depth + 1


class Story(Container):
    def __init__(self):
        super(Story, self).__init__()
        self.slug = ''
        self.title = ''
        self.__date = None
        self.author = ''
        self.__body = []
        self.comments = []
        self._timestamp = None
        self.rst_file = ''

    def __lt__(self, other):
        try:
            return self._timestamp <= other._timestamp
        except TypeError as e:
            print('-'*20)
            print(self.rst_file)
            print(self.slug)
            print(self.__body)
            print('='*20)
            raise e

    def __repr__(self):
        return '{0}: {1} at {2}, {3} comments'.format(
            self.slug, self.title, self.__date, len(self.comments))

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
        return '/{0:04d}/{1:02d}/{2:02d}/{3}/{4}'.format(
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
    def publish_date_rfc2822(self):
        return formatdate(float(self.__date.strftime('%s')))


def archive_directory(year_month):
    return os.path.join(
        '{0}'.format(config.settings.dir.output),
        'archive', year_month)


class Comment(Container):
    def __init__(self):
        super(Comment, self).__init__()
        self.commentator = ''
        self.url = ''
        self.create_date = None

    def add_content(self, content):
        self.__body.append(content)

    @property
    def contents(self):
        return self.__body


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
    pass


class Paragraph(Document):
    def __init__(self, *args, **kwargs):
        super(Paragraph, self).__init__(*args, **kwargs)
        self.text = ''


class Section(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(Section, self).__init__(*args, **kwargs)
        self.title = ''


class BulletList(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(BulletList, self).__init__(*args, **kwargs)


class EnumeratedList(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(EnumeratedList, self).__init__(*args, **kwargs)


class ListItem(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(ListItem, self).__init__(*args, **kwargs)


class Title(Document):
    def __init__(self, *args, **kwargs):
        super(Title, self).__init__(*args, **kwargs)
        self.text = ''

    def __repr__(self):
        return self.text


class Target(Document):
    def __init__(self):
        super(Target, self).__init__()
        self.ids = ''
        self.name = ''
        self.uri = ''


class Raw(Document):
    def __init__(self):
        super(Raw, self).__init__()
        self.format = ''
        self.text = ''


class Image(Document):
    def __init__(self):
        super(Image, self).__init__()
        self.alt = ''
        self.uri = ''
        self.width = None
        self.height = None


class BlockQuote(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(BlockQuote, self).__init__(*args, **kwargs)


class LiteralBlock(Document, Container, Nestable):
    def __init__(self, *args, **kwargs):
        super(LiteralBlock, self).__init__(*args, **kwargs)
        self.text = kwargs.get('text', '')


class Figure(Document, Container):
    def __init__(self, *args, **kwargs):
        super(Figure, self).__init__(*args, **kwargs)


class Caption(Document):
    def __init__(self, *args, **kwargs):
        super(Caption, self).__init__(*args, **kwargs)
        self.text = ''


class Table(Document, Container):
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.title = Title()


class ColSpec(Document):
    def __init__(self, *args, **kwargs):
        super(ColSpec, self).__init__(*args, **kwargs)
        self.width = None


class Row(Document, Container):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__(*args, **kwargs)


class Entry(Document, Container):
    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs)


class Transition(Document):
    def __init__(self, *args, **kwargs):
        super(Transition, self).__init__(*args, **kwargs)


class Topic(Document, Container):
    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        self.title = Title()


class SubstitutionDefinition(Document, Container):
    def __init__(self, *args, **kwargs):
        super(SubstitutionDefinition, self).__init__(*args, **kwargs)
        self.title = Title()
