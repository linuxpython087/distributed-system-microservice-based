from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from opentelemetry.instrumentation.sqlalchemy import (
    SQLAlchemyInstrumentor
)

from order_service.src.infrastructure.database import engine


def setup_tracing(app):

    resource = Resource.create({
        "service.name": "order-service"
    })

    provider = TracerProvider(
        resource=resource
    )

    trace.set_tracer_provider(
        provider
    )

    exporter = OTLPSpanExporter(
        endpoint="otel-collector:4317",
        insecure=True
    )

    provider.add_span_processor(
        BatchSpanProcessor(
            exporter
        )
    )

    FastAPIInstrumentor.instrument_app(app)

    SQLAlchemyInstrumentor().instrument(
        engine=engine
    )

    
# def setup_tracing(app):

#     resource = Resource.create({
#         "service.name": "order-service"
#     })

#     provider = TracerProvider(resource=resource)
#     trace.set_tracer_provider(provider)

#     otlp_exporter = OTLPSpanExporter(
#         endpoint="otel-collector:4317",
#         insecure=True
#     )

#     span_processor = BatchSpanProcessor(otlp_exporter)
#     provider.add_span_processor(span_processor)

#     FastAPIInstrumentor.instrument_app(app)

    