import pytest
from order_service.src.domain.value_objects.money import Money


def test_money_creation():
    m = Money(10, "USD")
    assert m.amount == 10
    assert m.currency == "USD"


def test_money_add():
    m1 = Money(10, "USD")
    m2 = Money(5, "USD")

    result = m1.add(m2)

    assert result.amount == 15


def test_money_negative():
    with pytest.raises(ValueError):
        Money(-10, "USD")


def test_money_multiply():
    m = Money(10, "USD")

    result = m.multiply(2)

    assert result.amount == 20
