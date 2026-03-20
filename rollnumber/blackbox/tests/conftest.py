import os
import uuid
from typing import Any, Dict

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("QUICKCART_BASE_URL", "http://localhost:8000/api/v1")


@pytest.fixture(scope="session")
def roll_number() -> str:
    return os.getenv("QUICKCART_ROLL_NUMBER", "1")


@pytest.fixture(scope="session")
def user_id() -> str:
    return os.getenv("QUICKCART_USER_ID", "1")


@pytest.fixture(scope="session")
def session() -> requests.Session:
    s = requests.Session()
    yield s
    s.close()


@pytest.fixture(scope="session")
def admin_headers(roll_number: str) -> Dict[str, str]:
    return {"X-Roll-Number": str(roll_number)}


@pytest.fixture(scope="session")
def user_headers(roll_number: str, user_id: str) -> Dict[str, str]:
    return {"X-Roll-Number": str(roll_number), "X-User-ID": str(user_id)}


@pytest.fixture(scope="session")
def json_headers(user_headers: Dict[str, str]) -> Dict[str, str]:
    headers = dict(user_headers)
    headers["Content-Type"] = "application/json"
    return headers


@pytest.fixture
def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def api_call(
    session: requests.Session,
    base_url: str,
    method: str,
    path: str,
    *,
    headers: Dict[str, str],
    **kwargs: Any,
) -> requests.Response:
    return session.request(
        method=method,
        url=f"{base_url}{path}",
        headers=headers,
        timeout=10,
        **kwargs,
    )


@pytest.fixture
def cart_clean(session: requests.Session, base_url: str, user_headers: Dict[str, str]):
    api_call(session, base_url, "DELETE", "/cart/clear", headers=user_headers)
    yield
    api_call(session, base_url, "DELETE", "/cart/clear", headers=user_headers)


@pytest.fixture
def profile_snapshot(session: requests.Session, base_url: str, user_headers: Dict[str, str]):
    resp = api_call(session, base_url, "GET", "/profile", headers=user_headers)
    resp.raise_for_status()
    original = resp.json()
    yield original

    restore_payload = {"name": original["name"], "phone": original["phone"]}
    api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers={**user_headers, "Content-Type": "application/json"},
        json=restore_payload,
    )


@pytest.fixture
def active_product_with_stock(
    session: requests.Session,
    base_url: str,
    user_headers: Dict[str, str],
) -> Dict[str, Any]:
    resp = api_call(
        session,
        base_url,
        "GET",
        "/products",
        headers=user_headers,
        params={"sort": "price_asc"},
    )
    resp.raise_for_status()
    products = resp.json()
    for product in products:
        if product.get("stock_quantity", 0) > 0:
            return product
    pytest.fail("No active product with stock available")


@pytest.fixture
def temp_address(
    session: requests.Session,
    base_url: str,
    json_headers: Dict[str, str],
    unique_suffix: str,
):
    payload = {
        "label": "HOME",
        "street": f"12345 Test Street {unique_suffix}",
        "city": "Pune",
        "pincode": "411001",
        "is_default": False,
    }
    create_resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json=payload,
    )
    create_resp.raise_for_status()
    data = create_resp.json()["address"]
    yield data

    api_call(
        session,
        base_url,
        "DELETE",
        f"/addresses/{data['address_id']}",
        headers=json_headers,
    )


@pytest.fixture
def created_order(
    session: requests.Session,
    base_url: str,
    json_headers: Dict[str, str],
    active_product_with_stock: Dict[str, Any],
):
    api_call(session, base_url, "DELETE", "/cart/clear", headers=json_headers)
    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": active_product_with_stock["product_id"], "quantity": 1},
    )
    add_resp.raise_for_status()

    checkout_resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "CARD"},
    )
    checkout_resp.raise_for_status()
    order = checkout_resp.json()
    yield {
        "order_id": order["order_id"],
        "product_id": active_product_with_stock["product_id"],
        "unit_price": active_product_with_stock["price"],
    }

    api_call(session, base_url, "DELETE", "/cart/clear", headers=json_headers)
