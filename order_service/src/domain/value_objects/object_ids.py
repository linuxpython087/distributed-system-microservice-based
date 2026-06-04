from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class BaseId:
    value: uuid.UUID

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_string(cls, value: str):
        return cls(uuid.UUID(value))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    @classmethod
    def new(cls):
        return cls(uuid.uuid4())


class UserId(BaseId):
    pass


class ProductId(BaseId):
    pass


class OrderId(BaseId):
    pass


class OrderItemId(BaseId):
    pass
