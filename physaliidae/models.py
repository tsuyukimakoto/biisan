import os
from email.utils import formatdate
import physaliidae_settings as settings


class Entry(object):
    def __init__(self, slug, published_from, title, body):
        self.slug = slug
        self.published_from = published_from
        self.title = title
        self.body = body
        self.comments = []
        self._timestamp = self.published_from.timestamp()

    def __lt__(self, other):
        return self._timestamp <= other._timestamp

    @property
    def directory(self):
        if not hasattr(self, '_directory'):
            self._directory = os.path.join(
                '{0}'.format(settings.dir.output),
                'blog',
                '{0:04d}'.format(self.published_from.year),
                '{0:02d}'.format(self.published_from.month),
                '{0:02d}'.format(self.published_from.day),
                self.slug
            )
        return self._directory

    @property
    def archive_directory(self):
        return os.path.join(
            '{0}'.format(settings.dir.output),
            'archive',
            '{0:04d}'.format(self.published_from.year),
            '{0}'.format(self.published_from.month)
        )

    @property
    def url(self):
        return '/{0:04d}/{1:02d}/{2:02d}/{3}/{4}'.format(
            self.published_from.year,
            self.published_from.month,
            self.published_from.day,
            self.slug,
            '')

    @property
    def publishd_date(self):
        return '{0:04d}-{1:02d}-{2:02d}/'.format(
            self.published_from.year,
            self.published_from.month,
            self.published_from.day)

    @property
    def publish_date_rfc2822(self):
        return formatdate(float(self.published_from.strftime('%s')))


def archive_directory(year_month):
    return os.path.join(
        '{0}'.format(settings.dir.output),
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
