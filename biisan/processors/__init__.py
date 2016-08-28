# import types
from datetime import datetime
import logging

from biisan.models import Comment

logger = logging.getLogger(__name__)


def process_field_name(elm, registry, entry):
    return elm.text


def process_field_body(elm, registry, entry):
    res = []
    for x in elm.getchildren():
        if 'field_list' == x.tag:
            print(x.tag)
        else:
            res.append(x.text)
    return res


def process_title(elm, registry, entry):
    entry.title = elm.text


def process_document(elm, registry, entry):
    for _elm in elm.getchildren():
        registry.process(_elm, entry)

def _process_comment(elm, registry, entry):
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
    c.body = body
    c.create_date = create_date
    entry.comments.append(c)


def process_docinfo(elm, registry, entry):
    for _elm in elm.getchildren():
        if len(_elm) == 2:
            if 'field_name' == _elm[0].tag:
                field_name = process_field_name(_elm[0], registry, entry)
                if field_name == 'slug':
                    entry.slug = process_field_body(
                        _elm[1], registry, entry)[0]
                elif field_name == 'author':
                    entry.author = process_field_body(
                        _elm[1], registry, entry)[0]
                elif field_name == 'comment':
                    _process_comment(_elm[1], registry, entry)
        elif 'date' == _elm.tag:
            entry.date = datetime.strptime(
                _elm.text, '%Y-%m-%d %H:%M'
            )
        elif 'author' == _elm.tag:
            entry.author = _elm.text


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

    def process(self, elm, entry):
        _processor_name = 'process_{0}'.format(elm.tag)
        if hasattr(self, _processor_name):
            logger.debug('---------------')
            logger.debug(getattr(self, _processor_name).__name__)
            logger.debug(getattr(self, _processor_name).__code__.co_varnames)
            return getattr(self, _processor_name)(elm, self, entry)
        else:
            logger.debug(
                'processor {0} is not defined and element ignored.'.format(
                    _processor_name))
