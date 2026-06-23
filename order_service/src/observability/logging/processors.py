import os
import traceback

SERVICE_NAME = "order-service"
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


from opentelemetry.trace import (
    get_current_span
)

def inject_trace(
    logger,
    method,
    event
):

    span = get_current_span()

    ctx = span.get_span_context()

    if ctx.is_valid:

        event["trace_id"] = (
            format(
                ctx.trace_id,
                "032x"
            )
        )

        event["span_id"] = (
            format(
                ctx.span_id,
                "016x"
            )
        )

    return event



def add_service_context(_, __, event_dict):

    event_dict["service"] = SERVICE_NAME
    event_dict["environment"] = ENVIRONMENT

    return event_dict


def add_exception(logger, method_name, event_dict):

    if "exception" in event_dict:

        event_dict["stack"] = traceback.format_exc()

    return event_dict
