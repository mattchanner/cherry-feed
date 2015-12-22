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
        'server.socket_port': int(os.environ.get('PORT', '5050')),
        'engine.autoreload.on': False,
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8'
    })

    cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize',
                                                 secure_headers,
                                                 priority=60)

    store = load_feed_store()

    web_app = webapp.WebApp()

    feed_api = feedapi.FeedApi(store)

    web_app.feeds = feed_api

    cherrypy.quickstart(web_app, '/', conf)
