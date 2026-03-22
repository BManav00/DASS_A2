import pytest

from conftest import api_call


@pytest.fixture
def non_existing_user_headers(admin_headers):
    return {**admin_headers, "X-User-ID": "999999"}


@pytest.mark.parametrize(
    "endpoint",
    [
        "/cart",
        "/wallet",
        "/orders",
        "/loyalty",
        "/support/tickets",
        "/addresses",
        "/products",
        "/products/1",
        "/products/1/reviews",
    ],
)
def test_non_existing_user_id_is_rejected_for_user_scoped_get_endpoints(
    session,
    base_url,
    non_existing_user_headers,
    endpoint,
):
    resp = api_call(
        session,
        base_url,
        "GET",
        endpoint,
        headers=non_existing_user_headers,
    )
    assert resp.status_code == 400


def test_cart_update_product_not_in_cart_returns_404(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/update",
        headers=json_headers,
        json={"product_id": 1, "quantity": 2},
    )
    assert resp.status_code == 404
