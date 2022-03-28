from datetime import datetime
import os
import tornado.ioloop
import tornado.options
from tornado.web import Application, StaticFileHandler
from flight_search import SearchFlightHandler
from airport_lookahead import AirportLookAheadHandler
from test_service import TestServiceHandler
from tornado_inst import BaseRequestHandler
import logging
logging.basicConfig()

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8080

def make_app():
    return tornado.web.Application([
        (r"/", TestServiceHandler),       
        (r"/flightsearchapi/searchflight", SearchFlightHandler),
        (r"/flightsearchapi/airportypeahead", AirportLookAheadHandler),
        (r"/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(LOCAL_DIR), "app_data"), "default_filename": "index.html"}),
    ])


tornado.options.parse_command_line()
app = make_app()
app.listen(PORT)
tornado.ioloop.IOLoop.current().start()



