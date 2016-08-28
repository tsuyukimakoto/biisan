import os
from email.utils import formatdate

from glueplate import config


class Entry(object):
    def __init__(self):
        self.slug = ''
        self.title = ''
        self.__date = None
        self.author = ''
        self.comments = []
        self._timestamp = None

    def __lt__(self, other):
        return self._timestamp <= other._timestamp

    def __repr__(self):
        return '{0}: {1} at {2}'.format(self.slug, self.title,
                                        self.__date)

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


class Comment(object):
    def __init__(self, *args):
        self.commentator, self.url, self.body, self.create_date = args


def next_entry(entry_list, i):
    if i >= len(entry_list) - 1:
        return '', ''
    target = entry_list[i + 1]
    return target.title, target.url


def previous_entry(entry_list, i):
    if i == 0:
        return '', ''
    target = entry_list[i - 1]
    return target.title, target.url
