import pytest

from conftest import api_call


@pytest.fixture
def non_existing_user_json_headers(admin_headers):
    return {
        **admin_headers,
        "X-User-ID": "999999",
        "Content-Type": "application/json",
    }


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/cart/add", {"product_id": 1, "quantity": 1}),
        ("POST", "/cart/update", {"product_id": 1, "quantity": 2}),
        ("POST", "/cart/remove", {"product_id": 1}),
        ("DELETE", "/cart/clear", None),
        ("POST", "/checkout", {"payment_method": "CARD"}),
        ("POST", "/wallet/add", {"amount": 1}),
        (
            "POST",
            "/support/ticket",
            {
                "subject": "Need Help",
                "message": "non-existing user must be rejected",
            },
        ),
        (
            "POST",
            "/addresses",
            {
                "label": "HOME",
                "street": "12345 Ghost Street",
                "city": "Pune",
                "pincode": "411001",
                "is_default": False,
            },
        ),
        (
            "POST",
            "/products/1/reviews",
            {"rating": 5, "comment": "review should fail for invalid user"},
        ),
    ],
)
def test_non_existing_user_id_is_rejected_for_user_scoped_write_endpoints(
    session,
    base_url,
    non_existing_user_json_headers,
    method,
    path,
    payload,
):
    kwargs = {"json": payload} if payload is not None else {}
    resp = api_call(
        session,
        base_url,
        method,
        path,
        headers=non_existing_user_json_headers,
        **kwargs,
    )

    assert resp.status_code == 400
    body = resp.json()
    assert isinstance(body, dict)
    assert "error" in body
