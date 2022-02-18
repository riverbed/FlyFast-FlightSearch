import os
from urllib.parse import urlparse

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
    def get(self):
       
        src = self.get_argument('from')
        dst = self.get_argument('to')

        self.span.update_binary_annotations({'sentresponseinjectedheader': self.span.zipkin_attrs.span_id})
        self.set_header("x-opnet-transaction-trace", self.span.zipkin_attrs.span_id)
        self.write("Sorry, no flights from {} to {} yet".format(src, dst))
        sendOTSpan()

def make_app():
    return tornado.web.Application([
        (r"/", TemplateHandler),       
        (r"/searchflight", SearchFlightHandler),
        (r"/(.*)", StaticFileHandler, {"path": os.path.join(LOCAL_DIR, "static"), "default_filename": "index.html"}),
    ])


tornado.options.parse_command_line()
app = make_app()
app.listen(8080)
tornado.ioloop.IOLoop.current().start()



