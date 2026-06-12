from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path", "status"],
)

ERROR_COUNT = Counter(
    "http_errors_total", "Total HTTP errors", ["method", "path", "status"]
)

ORDERS_CREATED = Counter("orders_created_total", "Total orders created")
