import logging
import os
from email.utils import formatdate
from hashlib import md5

from glueplate import config

from biisan.utils import get_environment

logger = logging.getLogger(__name__)


class Container:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__body = []

    def __append_to_body(self, content):
        pass

    def add_content(self, content):
        # if issubclass(content.__class__, Document):
        #     content.cnt = len(self.__body) + 1
        if isinstance(self, Nestable) and type(self) is type(content):
            content.depth = self.depth + 1
        self.__append_to_body(content)
        self.__body.append(content)

    @property
    def contents(self):
        return self.__body


class Nestable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = kwargs.get("depth", 1)


class HTMLize:
    env = get_environment(config)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_html(self):
        tmpl = HTMLize.env.get_template(os.path.join("components", f"{self.__class__.__name__}.html".lower()))
        return tmpl.render(element=self, config=config, hash_func=md5)


class Story(Container, HTMLize):
    def __init__(self):
        super().__init__()
        self.slug = ""
        self.title = ""
        self.__date = None
        self.author = ""
        self.__body = []
        self.comments = []
        self._timestamp = None
        self.source_file = ""
        self.extra = None
        self.additional_meta = {}

    def __lt__(self, other):
        try:
            return self._timestamp <= other._timestamp
        except TypeError as e:
            logger.error("-" * 20)
            logger.error(self.source_file)
            logger.error(self.slug)
            logger.error(self.__body)
            logger.error("=" * 20)
            raise e

    def __repr__(self):
        return f"{self.slug}: {self.title} at {self.__date}, {len(self.comments)} comments"

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, "additional_meta")[name]
        except KeyError:
            object.__getattribute__(self, name)

    def has_additional_meta(self, name):
        return hasattr(self, name)

    @property
    def date(self):
        if self.__date is None:
            raise ValueError("date must not be None.")
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date
        self._timestamp = self.__date.timestamp()

    @property
    def directory(self):
        if not hasattr(self, "_directory"):
            date = self.date
            self._directory = os.path.join(
                f"{config.settings.dir.output}",
                "blog",
                f"{date.year:04d}",
                f"{date.month:02d}",
                f"{date.day:02d}",
                self.slug,
            )
        return self._directory

    @property
    def archive_directory(self):
        date = self.date
        return os.path.join(
            f"{config.settings.dir.output}",
            "archive",
            f"{date.year:04d}",
            f"{date.month}",
        )

    @property
    def url(self):
        date = self.date
        return f"/blog/{date.year:04d}/{date.month:02d}/{date.day:02d}/{self.slug}/"

    @property
    def publishd_date(self):
        date = self.date
        return f"{date.year:04d}-{date.month:02d}-{date.day:02d}/"

    @property
    def published_datetime(self):
        date = self.date
        return f"{date.year:04d}/{date.month:02d}/{date.day:02d} {date.hour:02d}:{date.minute:02d}"

    @property
    def publish_date_rfc2822(self):
        return formatdate(self.date.timestamp())

    @property
    def publish_datetime_iso_8601(self):
        return self.date.isoformat()

    def prepare_html(self, story_list, i):
        self.prev_story = previous_story(story_list, i)
        self.next_story = next_story(story_list, i)

    def extra_directory(self, directory):
        self._directory = os.path.join(f"{config.settings.dir.output}", directory)


def archive_directory(year_month):
    return os.path.join(f"{config.settings.dir.output}", "archive", year_month)


class Comment(Container):
    def __init__(self):
        super().__init__()
        self.commentator = ""
        self.url = ""
        self.create_date = None

    # def add_content(self, content):
    #     self.__body.append(content)

    # @property
    # def contents(self):
    #     return self.__body

    @property
    def comemnted_datetime(self):
        date = self.create_date
        if date is None:
            raise ValueError("create_date must not be None.")
        return f"{date.year:04d}/{date.month:02d}/{date.day:02d} {date.hour:02d}:{date.minute:02d}"


def next_story(story_list, i):
    if i >= len(story_list) - 1:
        return "", ""
    target = story_list[i + 1]
    return target.title, target.url


def previous_story(story_list, i):
    if i == 0:
        return "", ""
    target = story_list[i - 1]
    return target.title, target.url


class Document:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnt = 0


class Paragraph(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ""

    @property
    def formated(self):
        # For inline elements that need text replacement
        _formated = self.text

        # First pass: replace text-based inline elements
        for content in self.contents:
            if isinstance(content, Strong):
                _formated = _formated.replace(content.text, f"<strong>{content.text}</strong>")
            elif isinstance(content, Emphasis):
                _formated = _formated.replace(content.text, f"<i>{content.text}</i>")
            elif isinstance(content, Literal):
                _formated = _formated.replace(content.text, f"<code>{content.text}</code>")
            elif isinstance(content, Reference):
                _name = content.name and content.name or content.text
                if content.text:  # Only replace if text exists
                    _formated = _formated.replace(content.text, f'<a href="{content.uri}">{_name}</a>')
            elif isinstance(content, Raw):
                if content.format == "html":
                    # HTML format: output as-is without wrapping
                    _formated = _formated.replace(content.text, content.text)
                else:
                    # Other formats: wrap in pre tag
                    _formated = _formated.replace(
                        content.text, f'<pre class="code {content.format}">{content.text}</pre>'
                    )

        # Second pass: append non-text elements (like images)
        for content in self.contents:
            if isinstance(content, Image):
                # Image doesn't have text to replace, so we append it
                _formated += content.to_html()
            elif not isinstance(content, (Strong, Emphasis, Literal, Reference, Raw)):
                logger.warning(f"Type:{type(content)} in paragraph doesn't treat.")

        return _formated


class Strong(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ""


class Emphasis(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ""


class Section(Document, Container, Nestable, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = ""


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
        self.text = ""

    def __repr__(self):
        return self.text or ""


class Target(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.ids = ""
        self.names = ""
        self.uri = ""


class Reference(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.uri = ""
        self.text = ""


class Literal(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.text = ""


class Raw(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.format = ""
        self.text = ""


class Image(Document, HTMLize):
    def __init__(self):
        super().__init__()
        self.alt = ""
        self.uri = ""
        self._width = None
        self._height = None

    @property
    def width(self):
        if not self._width:
            return ""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        if not self._height:
            return ""
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
        self.text = kwargs.get("text", "")


class Figure(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Caption(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ""


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
        self.colname = ""
        self.width = None
        self.scale = 100


class Row(Document, Container, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = False

    def to_html(self):
        if not self.header:
            return super().to_html()
        tmpl = HTMLize.env.get_template(os.path.join("components", f"header_{self.__class__.__name__}.html".lower()))
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
        self.text = kwargs.get("text", "")


class Definition(Document, Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DefinitionListItem(Document, HTMLize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.term = Term()
        self.definition = Definition()
