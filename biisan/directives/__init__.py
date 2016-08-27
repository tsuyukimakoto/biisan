from cgi import escape

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from glueplate import config


class PrismDirective(Directive):
    """
prism::
  :language: bash
    """

    directive_tag = 'prism'
    has_content = True
    option_spec = {'language': directives.unchanged}

    def run(self):
        css_class = ''
        if 'language' in self.options:
            css_class = 'language-{0}'.format(self.options['language'])
        self.assert_has_content()
        text = '<pre><code class="{0}">{1}</code></pre>'.format(
            css_class, self._get_escaped_content())
        return [nodes.raw('', text, format='html')]

    def _get_escaped_content(self):
        return '\n'.join(map(escape, self.content))


class NotesDirective(Directive):
    """
    """

    directive_tag = 'notes'
    has_content = True
    option_spec = {'date': directives.unchanged}

    def run(self):
        date_str = ''
        if 'date' in self.options:
            date_str = '({0})'.format(self.options['date'])
        self.assert_has_content()
        text = '''
<div class="notes">
  <blockquote class="last"><i class="icon-info"></i>{0} {1}</blockquote>
</div>'''.format(self._get_escaped_content(), date_str)
        return [nodes.raw('', text, format='html')]

    def _get_escaped_content(self):
        return '\n'.join(map(escape, self.content))


class AffDirective(Directive):
    """
aff::
  :asin: ASIN
  :title: title
  :aftag: tag
    """

    directive_tag = 'aff'
    has_content = True
    option_spec = {'asin': directives.unchanged, 'title': directives.unchanged}

    def run(self):
        _asin = '{0}'.format(self.options['asin'])
        _title = '{0}'.format(self.options['title'])
        self.assert_has_content()
        text = '''
<div class="row aff">
  <section class="one columns"></section>
  <section class="three columns">
  <img src="http://images-jp.amazon.com/images/P/{asin}.09.SZZZZZZZ.jpg">
  </section>
  <section class="eight columns">
  <a href="http://www.amazon.{tld}/gp/product/{asin}?tag={tag}">
    <h4>{title}</h4>
    <img
     src="http://ecx.images-amazon.com/images/G/09/buttons/buy-from-tan.gif" />
  </a>
  </section>
</div>'''.format(asin=_asin, title=_title,
                 tld=config.settings.directive.aff.tld,
                 tag=config.settings.directive.aff.tag)
        return [nodes.raw('', text, format='html')]
