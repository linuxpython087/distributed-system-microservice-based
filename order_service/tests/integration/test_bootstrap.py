from order_service.src.application.bootstrap import bootstrap
from order_service.src.application.services.message_bus import MessageBus


def test_bootstrap_returns_message_bus():
    bus = bootstrap(start_map=False)

    assert isinstance(bus, MessageBus)
