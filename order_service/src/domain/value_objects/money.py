from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)

    def _check_currency(self, other: "Money"):
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
