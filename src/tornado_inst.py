import os
from urllib.parse import urlparse
from uuid import uuid4
from tornado.web import RequestHandler, HTTPError
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_span_in_context
from opentelemetry import trace
from  opentelemetry.sdk.trace import Resource

from opentelemetry.trace.propagation import set_span_in_context

APP_NAME = "FlyFast-FlightSearch"

def get_hostname():
    
    url = os.environ.get("COLLECTOR_URL")
    urlParts = urlparse(url)
    hostname = "localhost"
    if urlParts.hostname is not None:
        hostname = urlParts.hostname
    return hostname

def get_otlp_tracer():
    hostname = get_hostname()
    span_exporter = OTLPSpanExporter(
            # optional     
        endpoint="http://{}:4317".format(hostname),
        # credentials=ChannelCredentials(credentials),
        # headers=(("metadata", "metadata")),
    )
    tracer_provider = TracerProvider(
        resource=Resource.create({
            "service.name": APP_NAME,            
        }),
    )
    trace.set_tracer_provider(tracer_provider)   
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    tracer = trace.get_tracer_provider().get_tracer("Flyfast-FlightSearch")   
    return tracer
    
tracer = get_otlp_tracer()
service_instance_id = str(uuid4())

def set_otlp_span_attributes(span):

    span.set_attribute("service.name", APP_NAME)       
    span.set_attribute("host.name", get_hostname())
    span.set_attribute("service.instance.id", service_instance_id)
    span.set_attribute("instrumentation.library.name", "opentelemetry")

class BaseRequestHandler(RequestHandler):
   
    def _execute(self, *args, **kwargs):

        self.otlp_span = tracer.start_span(self.request.path,
                            kind=trace.SpanKind.SERVER, )
        self.span_context = set_span_in_context(self.otlp_span)
        set_otlp_span_attributes(self.otlp_span)
        self.otlp_span.set_attribute("http.method", self.request.method)
        self.otlp_span.set_attribute("http.url", self.request.uri)        
        
        super(BaseRequestHandler, self)._execute(*args, **kwargs)
       
    def log_exception(self, typ, value, tb):
        if not isinstance(value, HTTPError) or 500 <= value.status_code <= 599:
            exception =(typ, value, tb)
            self.otlp_span.record_exception(exception)
            self.otlp_span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
            self.otlp_span.end()
        super(BaseRequestHandler, self).log_exception(typ, value, tb)

    def on_finish(self):
        self.otlp_span.set_attribute("sent.http.response.statuscode", self.get_status())
        
        self.otlp_span.end()
