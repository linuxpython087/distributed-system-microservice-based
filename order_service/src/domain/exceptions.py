class DomainException(Exception):
    pass


class OrderNotFound(DomainException):
    pass


class InvalidOrderState(DomainException):
    pass


class InvalidQuantity(DomainException):
    pass


class OrderItemNotFound(DomainException):
    pass


class CurrencyMismatch(DomainException):
    pass
