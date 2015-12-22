import cherrypy
from cherrypy.lib.static import serve_file
import os


class WebApp(object):
    """The top level web application handler."""

    expose = True

    @cherrypy.expose
    def index(self):
        """Returns the main index.html page."""
        index_path = os.path.abspath('public/index.html')
        return serve_file(index_path)
