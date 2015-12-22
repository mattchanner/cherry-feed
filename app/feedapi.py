"""
  The MIT License (MIT)
  Copyright 2015 Matt Channer (mchanner at gmail dot com)

  Permission is hereby granted, free of charge, to any person obtaining a
  copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation
  the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""
import cherrypy
import json


class FeedApi(object):
    """Provides an API for feed data."""

    exposed = True

    def __init__(self, feed_model):
        self.feed_model = feed_model

    def _json(self, model):
        """Helper to return JSON data."""
        cherrypy.response.headers['Content-Type'] = "application/json"
        return json.dumps(model)

    def _html(self, html):
        """Helper to an HTML document from a summary fragment."""

        # Could use a Jinja2 template here but seems overkill
        cherrypy.response.headers['Content-Type'] = "text/html"

        doc = """
            <html>
                <head>
                    <link rel='stylesheet'
                          href='/lib/bootstrap-3/css/bootstrap.css'>
                </head>
                <body>
                    {}
                </body>
            </html>""".format(html)
        print doc
        return str(doc)

    def GET(self, id=None, item_index=None):
        """Main feed handler.
           Supports the following URL patterns:
           GET /feeds              Returns an array of all feeds
           GET /feeds/<uuid>       Returns the links and top level feed details
                                   for a single feed
           GET /feeds/<uuid>/index Returns the summary data for a single
                                   feed entry
        """
        if not id:
            # /feeds
            return self._json(self.feed_model.feeds())

        feed_data = self.feed_model.feed_by_id(id)
        if not item_index:
            # /feeds/<uuid>
            return self._json(feed_data)
        else:
            # /feeds/<uuid>/<feed_index>
            item = feed_data['data']['items'][int(item_index)]
            return self._html(item['summary'])
