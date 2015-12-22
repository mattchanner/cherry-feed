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
