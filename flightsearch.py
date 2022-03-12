from datetime import datetime
import os
import random
from xmlrpc.client import DateTime
import tornado.ioloop
import tornado.options
from tornado.web import Application, StaticFileHandler
from tornado.template import Template
from zipkin import get_zipkin_url
from zipkin.tornado import BaseRequestHandler
import logging
logging.basicConfig()
import time
import simplejson as json
from datetime import timedelta
import database.findAirport


LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

class TemplateHandler(BaseRequestHandler):
    def get(self):
        with open(os.path.join(LOCAL_DIR, "templates", "index.html.template"), "r") as infile:
            template = Template(infile.read())
        self.write(template.generate(zipkin_url=get_zipkin_url()))        

class SearchFlightHandler(BaseRequestHandler):
    
    def make_flight(self, returnFlightDate, src, dst, seatType = 'Economy'):
        flight = {}
        returnDate = time.strptime(returnFlightDate, "%m-%d-%Y")
        departureTime = datetime(returnDate.tm_year, returnDate.tm_mon, returnDate.tm_mday)
        flight["departureTime"] = departureTime.strftime("%m-%d-%Y, %H:%M")
        flight["arrivalTime"] = (departureTime +  timedelta(days=0, hours=3)).strftime("%m-%d-%Y, %H:%M")
        flight["from"] = src
        flight["to"] = dst
        flight["seat"] = seatType
        
        seed = str(flight)       
        random.seed(seed)
        flight["fare"] = random.randint(75, 1000)
        random.seed(seed)
        flight["flightNumber"] = random.randint(100, 1000)
        return flight

    def handle_request_post_n_get(self):
      
        flights = []
        searchParams  = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
        print ("flight search parameters received: " + searchParams)

        departure = datetime.now().strftime("%m-%d-%Y")
        if 'departure' in searchParams:
             departure = self.get_argument('departure')

        seatype = 'Economy'
        if 'seat' in searchParams:
             seatype = self.get_argument('seat')

        foundFlight = self.make_flight(departure, self.get_argument('from'), self.get_argument('to'), seatype)        
        flights.append(foundFlight)
        
        if 'return' in searchParams:
            print("round trip")
            returnFlight = self.make_flight(self.get_argument('return'), self.get_argument('to'), self.get_argument('from'), seatype)
            flights.append(returnFlight)

        # self.span.update_binary_annotations({'sentresponseinjectedheader': self.span.zipkin_attrs.span_id})
        # self.set_header("x-opnet-transaction-trace", self.span.zipkin_attrs.span_id)       
        result = json.dumps(flights)
        self.write(result)
        

    def get(self):       
       self.handle_request_post_n_get()
        
    def post(self):
        self.handle_request_post_n_get()


class AirportLookAheadHandler(BaseRequestHandler):
    
    def handle_request_post_n_get(self):
        
        searchParams  = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
        searchTxt = self.get_argument('searchtxt')
        limit = 15
        if 'limit' in searchParams:
            limit = self.get_argument('limit')
        # self.span.update_binary_annotations({'sentresponseinjectedheader': self.span.zipkin_attrs.span_id})
        # self.set_header("x-opnet-transaction-trace", self.span.zipkin_attrs.span_id)
        airports = database.findAirport.find_airports_containing(searchTxt, limit)        
        self.write(airports)

    def get(self):       
       self.handle_request_post_n_get()
        
    def post(self):
        self.handle_request_post_n_get()    

def make_app():
    return tornado.web.Application([
        (r"/", TemplateHandler),       
        (r"/flightsearchapi/searchflight", SearchFlightHandler),
        (r"/flightsearchapi/airportypeahead", AirportLookAheadHandler),
        (r"/(.*)", StaticFileHandler, {"path": os.path.join(LOCAL_DIR, "static"), "default_filename": "index.html"}),
    ])


tornado.options.parse_command_line()
app = make_app()
app.listen(8080)
tornado.ioloop.IOLoop.current().start()



