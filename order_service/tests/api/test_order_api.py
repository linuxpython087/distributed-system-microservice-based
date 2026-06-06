from fastapi.testclient import TestClient
from order_service.src.interfaces.api.app import app

client = TestClient(app)

def test_create_order_api():
    response = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    })

    assert response.status_code == 201
    assert "order_id" in response.json()



def test_add_item_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    response = client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 2,
        "unit_price": 10
    })

    assert response.status_code == 201
    assert "Item Added" in response.json().get('message')


def test_confirm_order_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 1,
        "unit_price": 10
    })

    response = client.post(f"/orders/{order_id}/confirm")

    assert response.status_code == 201


def test_confirm_empty_order_fails():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    response = client.post(f"/orders/{order_id}/confirm")

    assert response.status_code == 409




def test_cancle_order_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 1,
        "unit_price": 10
    })

    response = client.post(f"/orders/{order_id}/cancel")

    assert response.status_code == 204




def test_confirm_and_cancle_order_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 1,
        "unit_price": 10
    })
    response = client.post(f"/orders/{order_id}/confirm")

    response = client.post(f"/orders/{order_id}/cancel")

    assert response.status_code == 204


def test_cancle_empty_order_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    

    response = client.post(f"/orders/{order_id}/cancel")

    assert response.status_code == 204


def test_remove_item_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    item = client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 2,
        "unit_price": 10
    })

    item_id = item.json()["item_id"]

    response = client.delete(f"/orders/{order_id}/items/{item_id}")

    assert response.status_code == 204



def test_change_quantity_api():
    order = client.post("/orders/", json={
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }).json()

    order_id = order["order_id"]

    item = client.post(f"/orders/{order_id}/items", json={
        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "qty": 2,
        "unit_price": 10
    })

    item_id = item.json()["item_id"]

    response = client.patch(
        f"/orders/{order_id}/items/{item_id}/quantity",
        json={"qty": 5}
    )

    assert response.status_code == 202
    assert response.json()["message"] == "quantity updated"