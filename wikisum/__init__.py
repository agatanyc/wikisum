#!/usr/bin/env python3
"""This project defines a small HTTP server to serve descriptions of Wikipedia
pages.  To fetch a description of a certain page, submit a GET request to route
`/page/:id`, where `:id` is the numeric ID of the desired page.  If the server
is run with the `-t` flag, it serves only canned data.

For convenience, in non-test mode, page names may be used in preference to
numeric IDs; e.g., `/page/New_york_city` rather than `/page/645042`.
"""

# Standard library
from collections import namedtuple
from sys         import argv

# Third-party libraries
from bleach      import clean           # sanitizes HTML
from flask       import Flask, abort    # serves and routes HTTP
from wikipedia   import page as wiki    # wraps Wikipedia's MediaWiki API

# Test Support ----------------------------------------------------------------

MockPage = namedtuple("MockPage",
    "url title pageid parent_id revision_id content sections summary".split())

mock_pages = { mp.pageid: mp for mp in [
    MockPage("http://en.wikipedia.org/wiki/Krak%C3%B3w",
        "Kraków", "16815", "657359058", "658830708", "", "", ""),
    MockPage("http://en.wikipedia.org/wiki/New_york_city",
        "New York City", "645042", "658917492", "658950766", "", "", "")] }

# Wikipedia Access ------------------------------------------------------------

def get_page(id):
    return wiki(pageid=int(id)) if id.isnumeric() else wiki(id)

# HTML Generation -------------------------------------------------------------

def mkdoc(page):
    """Return a structure representing an HTML document summarizing the
    specified Wikipedia page.
    """
    return ['html',
            ['head',
              '<meta content="text/html; charset=utf-8"' +
              ' http-equiv="content-type" />',
              ['title', "Report: " + clean(page.title)],
              ['style', 'table, td, th, tr { border: 1px solid black }']],
            ['body',
              ['table'] + [
                ['tr',
                  ['th', h],
                  ['td', clean(d)]
                ] for h, d in (
                  ('Title'       , page.title       ),
                  ('URL'         , page.url         ),
                  ('Page ID'     , page.pageid      ),
                  ('Parent ID'   , page.parent_id   ),
                  ('Revision ID' , page.revision_id ),
                  ('Content'     , page.content     ),
                  ('Sections'    , page.sections    ),
                  ('Summary'     , page.summary     ))]]]

def mktag(name, contents):
    """Return a string of HTML containing a tag with the specified `name` and
    `contents`.
    """
    return '<{}>{}</{}>'.format(name, '\n'.join(contents), name)

def render_html(element):
    """Return a string of HTML.  If `element` is a string, it is returned
    unchanged; else, it must be a list representing a tag.  The first item in
    the list is the tag's name, and the remaining items are its contents.  The
    contents are automatically rendered by `render_html` (recursively).
    """
    return element if type(element) == str \
      else mktag(element[0], map(render_html, element[1:]))

# Main ------------------------------------------------------------------------

if __name__ == '__main__':

    app = Flask("wikisum")

    @app.route("/page/<id>")
    def summarize(id):
        print("Processing", id)
        try:
            page = mock_pages[id] if '-t' in argv else get_page(id)
            return render_html(mkdoc(page))
        except Exception as error:
            abort(404)

    app.run()
