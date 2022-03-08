# /**********************************/
# /*       Copyright (c) 2021       */
# /*         Aternity, Inc.         */
# /*      All Rights Reserved.      */
# /**********************************/

from urllib.parse import urlparse
from tornado.web import RequestHandler, HTTPError

from py_zipkin.zipkin import zipkin_span
from py_zipkin import Encoding, Kind
from py_zipkin.util import ZipkinAttrs

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.trace import set_span_in_context
from opentelemetry import trace
from  opentelemetry.sdk.trace import Resource

from . import get_transport, get_zipkin_url

app_name = "FlyFast-FlightSearch"

def create_zipkin_attrs_from_tornado_request(request):
    zipkin_attrs = None

    trace_id = request.headers.get("X-B3-TraceId")
    if trace_id is not None:
        span_id = request.headers.get("X-B3-SpanId")
        parent_span_id = request.headers.get("X-B3-ParentSpanId")
        print(trace_id + ":" + span_id + ":" + parent_span_id)
        flags = request.headers.get("X-B3-Flags", "0")
        sample_str = request.headers.get("X-B3-Sampled", "1")

        sampled = False
        if sample_str in ("1", "d"):
            sampled = True

        zipkin_attrs = ZipkinAttrs(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            flags = flags,
            is_sampled=sampled
        )

    return zipkin_attrs


def create_span_from_tornado_request(request):
    zipkin_attrs = create_zipkin_attrs_from_tornado_request(request)
    span_name = request.path
    request_headers = [{"key": key, "value": value} for key, value in request.headers.items()]
    return zipkin_span(
        sample_rate=100.0,
        service_name= app_name,
        span_name=span_name,
        transport_handler=get_transport(),
        encoding=Encoding.V2_JSON,
        binary_annotations={"request.headers": request_headers},
        kind=Kind.SERVER,
        zipkin_attrs=zipkin_attrs,
    )


def get_hostname():
    zipkinUrl = get_zipkin_url()
    urlParts = urlparse(zipkinUrl)
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
            "service.name": app_name,            
        }),
    )
    trace.set_tracer_provider(tracer_provider)   
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    tracer = trace.get_tracer_provider().get_tracer(__name__)   
    return tracer
    
tracer = get_otlp_tracer()

class BaseRequestHandler(RequestHandler):
   
    def _execute(self, *args, **kwargs):
        self.span = create_span_from_tornado_request(self.request)
        self.span.start()

        self.otlp_span = tracer.start_span(self.request.path,
                            kind=trace.SpanKind.SERVER,
                            attributes={
                                "http.method": self.request.method,
                                "http.url": self.request.uri,
                                "service.name": app_name
                            },)
        
        self.otlp_span.set_attribute("service.name", app_name)
        super(BaseRequestHandler, self)._execute(*args, **kwargs)
       
    def log_exception(self, typ, value, tb):
        if not isinstance(value, HTTPError) or 500 <= value.status_code <= 599:
            self.span.update_binary_annotations({'error': True})
            self.span.stop(typ, value, tb)
            self.otlp_span.end()
        super(BaseRequestHandler, self).log_exception(typ, value, tb)

    def on_finish(self):
        self.span.update_binary_annotations({'http.status_code': self.get_status()})
        self.span.stop()
        self.otlp_span.end()
