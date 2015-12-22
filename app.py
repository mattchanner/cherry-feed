import cherrypy
import os
import json

from app import webapp, feedapi
from models import feeds


def load_feed_store():
    """Loads the list of feeds from a JSON data source."""
    feed_file = os.path.abspath('data/feeds.json')
    with open(feed_file, 'r') as f:
        feed_data = json.load(f)
        store = feeds.FeedStore(feed_data)
        return store


def secure_headers():
    """Sets secure headers on each response."""
    headers = cherrypy.response.headers
    headers['Cache-Control'] = 'no-cache, no-store, private, mustrevalidate'
    headers['Pragma'] = 'no-cache'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"


if __name__ == "__main__":
    conf = {
        '/': {
            'tools.secureheaders.on': True
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.abspath('public/favicon.png')
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('public/js')
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('public/css')
        },
        '/lib': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('public/lib')
        },
        '/feeds': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', '5050'))
    })

    cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize',
                                                 secure_headers,
                                                 priority=60)

    store = load_feed_store()

    web_app = webapp.WebApp()

    feed_api = feedapi.FeedApi(store)

    web_app.feeds = feed_api

    cherrypy.quickstart(web_app, '/', conf)
