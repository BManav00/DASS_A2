from conftest import api_call


def test_cart_add_zero_quantity_rejected(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 0},
    )
    assert resp.status_code == 400


def test_cart_add_negative_quantity_rejected(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": -1},
    )
    assert resp.status_code == 400


def test_cart_add_product_not_found_returns_404(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 999999, "quantity": 1},
    )
    assert resp.status_code == 404


def test_cart_add_insufficient_stock_returns_400(session, base_url, json_headers, cart_clean):
    product_resp = api_call(session, base_url, "GET", "/products/1", headers=json_headers)
    assert product_resp.status_code == 200
    stock = product_resp.json()["stock_quantity"]

    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": stock + 1},
    )
    assert resp.status_code == 400


def test_cart_add_same_product_accumulates_quantity(session, base_url, json_headers, cart_clean):
    first = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 2},
    )
    second = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 3},
    )
    assert first.status_code == 200
    assert second.status_code == 200

    cart_resp = api_call(session, base_url, "GET", "/cart", headers=json_headers)
    assert cart_resp.status_code == 200
    item = [i for i in cart_resp.json()["items"] if i["product_id"] == 1][0]
    assert item["quantity"] == 5


def test_cart_subtotal_and_total_are_exact(session, base_url, json_headers, cart_clean):
    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 2},
    )
    assert add_resp.status_code == 200

    cart_resp = api_call(session, base_url, "GET", "/cart", headers=json_headers)
    assert cart_resp.status_code == 200
    cart = cart_resp.json()

    first_item = cart["items"][0]
    expected_subtotal = first_item["quantity"] * first_item["unit_price"]
    assert first_item["subtotal"] == expected_subtotal

    expected_total = sum(item["subtotal"] for item in cart["items"])
    assert cart["total"] == expected_total


def test_cart_update_zero_quantity_rejected(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/update",
        headers=json_headers,
        json={"product_id": 1, "quantity": 0},
    )
    assert resp.status_code == 400


def test_cart_remove_non_existing_product_returns_404(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/remove",
        headers=json_headers,
        json={"product_id": 999999},
    )
    assert resp.status_code == 404


def test_coupon_expired_coupon_rejected(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/coupon/apply",
        headers=json_headers,
        json={"coupon_code": "DEAL5"},
    )
    assert resp.status_code == 400


def test_coupon_min_cart_value_enforced(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/coupon/apply",
        headers=json_headers,
        json={"coupon_code": "BONUS75"},
    )
    assert resp.status_code == 400


def test_checkout_empty_cart_rejected(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "COD"},
    )
    assert resp.status_code == 400


def test_checkout_invalid_payment_method_rejected(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "UPI"},
    )
    assert resp.status_code == 400


def test_checkout_cod_over_5000_rejected(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 50},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "COD"},
    )
    assert resp.status_code == 400


def test_checkout_gst_added_once(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 27, "quantity": 1},
    )

    resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "CARD"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["gst_amount"] == 1
    assert body["total_amount"] == 21
