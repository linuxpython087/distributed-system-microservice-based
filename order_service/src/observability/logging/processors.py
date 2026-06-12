import os
import traceback

SERVICE_NAME = "order-service"
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


def add_service_context(_, __, event_dict):

    event_dict["service"] = SERVICE_NAME
    event_dict["environment"] = ENVIRONMENT

    return event_dict


def add_exception(logger, method_name, event_dict):

    if "exception" in event_dict:

        event_dict["stack"] = traceback.format_exc()

    return event_dict
