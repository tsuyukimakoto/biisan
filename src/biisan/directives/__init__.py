import logging
from html import escape

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from glueplate import config

logger = logging.getLogger(__name__)


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
            css_class = f'language-{self.options["language"]}'
        self.assert_has_content()
        text = f'<pre><code class="{css_class}">{self._get_escaped_content()}</code></pre>'
        return [nodes.raw('', text, format='html')]

    def _get_escaped_content(self):
        return '\n'.join(map(escape, self.content))


class NotesDirective(Directive):
    """ """

    directive_tag = 'notes'
    has_content = True
    option_spec = {'date': directives.unchanged}

    def run(self):
        date_str = ''
        if 'date' in self.options:
            date_str = f'({self.options["date"]})'
        self.assert_has_content()
        text = f"""
<div class="notes">
  <blockquote class="last"><i class="icon-info"></i>{self._get_escaped_content()} {date_str}</blockquote>
</div>"""
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
    option_spec = {
        'asin': directives.unchanged,
        'title': directives.unchanged,
        'image_url': directives.unchanged,
    }

    def run(self):
        _asin = str(self.options['asin'])
        _title = str(self.options['title'])
        self.assert_has_content()
        _image_url = self.options.get('image_url', None)
        if _image_url:
            _image_url = f'<img src="{_image_url}">'
        else:
            _image_url = '<img src="http://images-jp.amazon.com/images/P/{asin}.09.SZZZZZZZ.jpg">'.format(
                asin=self.options['asin'],
            )
        text = """
<div class="biisan-aff">
  <fieldset>
    <legend>{title}</legend>
    <div class="biisan-aff-container">
      <div class="biisan-aff-amz">
        <p>{image_url}</p>
      </div>
      <div class="biisan-aff-content">
        <h4>{title}</h4>
      {contents}
        <p>
          <a href="http://www.amazon.{tld}/gp/product/{asin}?tag={tag}">
            <img
            src="http://ecx.images-amazon.com/images/G/09/buttons/buy-from-tan.gif" />
          </a>
        </p>
      </div>
    </div>
  </fieldset>
</div>""".format(
            asin=_asin,
            title=_title,
            image_url=_image_url,
            tld=config.settings.directive.aff.tld,
            tag=config.settings.directive.aff.tag,
            contents='<br />'.join(self.content),
        )
        return [nodes.raw('', text, format='html')]


class AppleAffButtonDirective(Directive):
    """
    appleaff::
      :url: permalink
      :shop: appstore / macappstore / itunes / music
    """

    directive_tag = 'appleaff'
    has_content = False
    option_spec = {'at': directives.unchanged, 'url': directives.unchanged, 'shop': directives.unchanged}
    shop_type_button = {
        'appstore': 'https://linkmaker.itunes.apple.com/images/badges/ja-jp/badge_appstore-lrg.svg',
        'macappstore': 'https://linkmaker.itunes.apple.com/images/badges/ja-jp/badge_macappstore-lrg.svg',
        'itunes': 'https://linkmaker.itunes.apple.com/images/badges/ja-jp/badge_itunes-lrg.svg',
        'music': 'https://linkmaker.itunes.apple.com/images/badges/ja-jp/badge_music-lrg.svg',
    }

    def get_shop(self, shop_type):
        assert shop_type in AppleAffButtonDirective.shop_type_button
        return AppleAffButtonDirective.shop_type_button[shop_type]

    def run(self):
        _url = str(self.options['url'])
        _shop = str(self.options['shop'])
        _shop_button = self.get_shop(_shop)
        _affurl = '?' in _url and '{0}&at={1}' or '{0}?at={1}'
        _affurl = _affurl.format(_url, config.settings.directive.appleaff.at)
        text = f"""<a class="biisan-apple-aff" href="{_affurl}"><img
  src="{_shop_button}" /></a>"""
        return [nodes.raw('', text, format='html')]
