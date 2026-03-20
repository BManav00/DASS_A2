from conftest import api_call


def test_cart_add_update_remove_and_clear_success(
    session,
    base_url,
    json_headers,
    active_product_with_stock,
    cart_clean,
):
    get_resp = api_call(session, base_url, "GET", "/cart", headers=json_headers)
    assert get_resp.status_code == 200

    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": active_product_with_stock["product_id"], "quantity": 1},
    )
    assert add_resp.status_code == 200

    update_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/update",
        headers=json_headers,
        json={"product_id": active_product_with_stock["product_id"], "quantity": 2},
    )
    assert update_resp.status_code == 200

    cart_resp = api_call(session, base_url, "GET", "/cart", headers=json_headers)
    assert cart_resp.status_code == 200
    items = cart_resp.json()["items"]
    assert len(items) >= 1

    remove_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/remove",
        headers=json_headers,
        json={"product_id": active_product_with_stock["product_id"]},
    )
    assert remove_resp.status_code == 200

    clear_resp = api_call(session, base_url, "DELETE", "/cart/clear", headers=json_headers)
    assert clear_resp.status_code == 200


def test_coupon_apply_and_remove_success(
    session,
    base_url,
    json_headers,
    cart_clean,
):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    apply_resp = api_call(
        session,
        base_url,
        "POST",
        "/coupon/apply",
        headers=json_headers,
        json={"coupon_code": "WELCOME50"},
    )
    assert apply_resp.status_code == 200
    apply_body = apply_resp.json()
    assert apply_body["coupon_code"] == "WELCOME50"
    assert "discount" in apply_body
    assert "new_total" in apply_body

    remove_resp = api_call(session, base_url, "POST", "/coupon/remove", headers=json_headers)
    assert remove_resp.status_code == 200


def test_checkout_card_success(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 1},
    )

    checkout_resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "CARD"},
    )
    assert checkout_resp.status_code == 200
    body = checkout_resp.json()
    assert body["payment_status"] == "PAID"
    assert body["order_status"] == "PLACED"


def test_checkout_wallet_success(session, base_url, json_headers, cart_clean):
    api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 27, "quantity": 1},
    )

    checkout_resp = api_call(
        session,
        base_url,
        "POST",
        "/checkout",
        headers=json_headers,
        json={"payment_method": "WALLET"},
    )
    assert checkout_resp.status_code == 200
    body = checkout_resp.json()
    assert body["payment_status"] == "PENDING"
    assert body["order_status"] == "PLACED"


def test_orders_detail_invoice_and_cancel_success(
    session,
    base_url,
    json_headers,
    created_order,
):
    order_id = created_order["order_id"]

    list_resp = api_call(session, base_url, "GET", "/orders", headers=json_headers)
    assert list_resp.status_code == 200
    orders = list_resp.json()
    assert any(o["order_id"] == order_id for o in orders)

    detail_resp = api_call(session, base_url, "GET", f"/orders/{order_id}", headers=json_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["order_id"] == order_id
    assert "items" in detail

    invoice_resp = api_call(
        session,
        base_url,
        "GET",
        f"/orders/{order_id}/invoice",
        headers=json_headers,
    )
    assert invoice_resp.status_code == 200
    invoice = invoice_resp.json()
    assert float(invoice["subtotal"]) + float(invoice["gst_amount"]) == float(invoice["total_amount"])

    cancel_resp = api_call(
        session,
        base_url,
        "POST",
        f"/orders/{order_id}/cancel",
        headers=json_headers,
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["order_status"] == "CANCELLED"


def test_post_review_success(session, base_url, json_headers, unique_suffix):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 5, "comment": f"Great item {unique_suffix}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Review added successfully"
    assert "review_id" in body
