from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class BaseId:
    value: uuid.UUID

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_string(cls, value):
        if isinstance(value, cls):
            return value
        return cls(uuid.UUID(str(value)))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    @classmethod
    def new(cls):
        return cls(uuid.uuid4())
    

    

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other):
        return self.value < other.value  # IMPORTANT


class UserId(BaseId):
    pass


class ProductId(BaseId):
    pass


class OrderId(BaseId):
    pass


class OrderItemId(BaseId):
    pass


class IdempotencyId(BaseId):
    pass


class EventId(BaseId):
    pass


class OutboxId(BaseId):
    pass