My First Blog
================================================================

:slug: my_first_blog
:date: 2019-04-06 11:06
:author: makoto tsuyuki

:comment:
  :commentator: コメンテータ
  :url: https://www.example.com/testurl
  :body: コメント1行目
    コメント2行目
  :create_date: 2019-05-04 22:45


This is my first Blog
-------------------------------------------

test **paragraph!** has *my word*.

- This is a bullet list.
- bullet2

1. This is an enumerated list.
1. Enumerators may be arabic numbers, letters, or roman
   numerals.

Directives
-------------------------------------------

.. prism::
   :language: python

   >>> import zen

.. notes::
   :date: 2019-04-13

   ノート

.. aff::
  :asin: testasin
  :title: 素敵な商品

  ほげほげ

.. appleaff::
  :url: https://example.com
  :shop: macappstore

.. topic:: Topic Title

  トピック本文1行目
  トピック本文2行目

.. [1] A footnote contains body elements

.. [CIT2002] Just like a footnote,

Goto `Python`_

.. _`Python`: https://www.python.org

.. image:: biisan.png

.. figure:: larch.png

   Caption

.. |symbol here| image:: symbol.png

.. Comments

Definition List and ...
-------------------------------------------

term
  description is here.

:field list: Field lists map field names to field bodies.

-a  option list

Literal block::

  this is literal

Block quotes:

  This is block quotes.

Table
-------------------------------------------

.. csv-table::
  :header: "column1", "column2"

  "data11", "data21"
  "data12", "data22"

Raw
-------------------------------------------

.. raw:: html

  <div>hello world</div>

Transition
-------------------------------------------

パラグラフ1

----------

パラグラフ2
