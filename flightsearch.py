from datetime import datetime
import os
import random
from urllib.parse import urlparse
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
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

import simplejson as json
from datetime import timedelta
import database.findAirport

zipkinUrl = get_zipkin_url()
urlParts = urlparse(zipkinUrl)
hostname = "localhost"
if urlParts.hostname is not None:
    hostname = urlParts.hostname

span_exporter = OTLPSpanExporter(
        # optional     
     endpoint="http://{}:4317".format(hostname),
    # credentials=ChannelCredentials(credentials),
    # headers=(("metadata", "metadata")),
)

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)
tracer = trace.get_tracer_provider().get_tracer(__name__)
count = 0

def sendOTSpan():
    global count
    span = "span" + str(count)
    with tracer.start_as_current_span(span):
        print("sent OT span: " + span)
        count = count + 1

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

class TemplateHandler(BaseRequestHandler):
    def get(self):
        with open(os.path.join(LOCAL_DIR, "templates", "index.html.template"), "r") as infile:
            template = Template(infile.read())
        self.write(template.generate(zipkin_url=get_zipkin_url()))
        sendOTSpan()


class SearchFlightHandler(BaseRequestHandler):
    
    def make_flight(self, returnFlightDate, src, dst, seatType = 'Economy'):
        flight = {}

        returnDate = time.strptime(returnFlightDate, "%m/%d/%Y")
        departureTime = datetime(returnDate.tm_year, returnDate.tm_mon, returnDate.tm_mday)
        flight["departureTime"] = departureTime.strftime("%m/%d/%Y, %H:%M")
        flight["arrivalTime"] = (departureTime +  timedelta(days=0, hours=3)).strftime("%m/%d/%Y, %H:%M")
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

        departure = datetime.now().strftime("%m/%d/%Y")

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

        self.span.update_binary_annotations({'sentresponseinjectedheader': self.span.zipkin_attrs.span_id})
        self.set_header("x-opnet-transaction-trace", self.span.zipkin_attrs.span_id)       
        result = json.dumps(flights)
        self.write(result)
        sendOTSpan()

    def get(self):       
       self.handle_request_post_n_get()
        
    def post(self):
        self.handle_request_post_n_get()


class AirportLookAheadHandler(BaseRequestHandler):
    
    def handle_request_post_n_get(self):
        
        searchTxt = self.get_argument('searchtxt')
        self.span.update_binary_annotations({'sentresponseinjectedheader': self.span.zipkin_attrs.span_id})
        self.set_header("x-opnet-transaction-trace", self.span.zipkin_attrs.span_id)
        airports = database.findAirport.find_airports_containing(searchTxt)        
        self.write(airports)
        sendOTSpan()

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



