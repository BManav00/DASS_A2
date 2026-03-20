import pytest

from conftest import api_call


def test_wallet_add_invalid_amounts_rejected(session, base_url, json_headers):
    zero_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/add",
        headers=json_headers,
        json={"amount": 0},
    )
    assert zero_resp.status_code == 400

    over_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/add",
        headers=json_headers,
        json={"amount": 100001},
    )
    assert over_resp.status_code == 400


def test_wallet_pay_must_deduct_exact_amount(session, base_url, json_headers):
    before_resp = api_call(session, base_url, "GET", "/wallet", headers=json_headers)
    assert before_resp.status_code == 200
    before = float(before_resp.json()["wallet_balance"])

    topup_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/add",
        headers=json_headers,
        json={"amount": 10},
    )
    assert topup_resp.status_code == 200

    pay_amount = 5
    pay_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/pay",
        headers=json_headers,
        json={"amount": pay_amount},
    )
    assert pay_resp.status_code == 200

    after_resp = api_call(session, base_url, "GET", "/wallet", headers=json_headers)
    assert after_resp.status_code == 200
    after = float(after_resp.json()["wallet_balance"])

    deducted = (before + 10) - after
    assert abs(deducted - pay_amount) < 1e-9


def test_wallet_pay_insufficient_balance_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/pay",
        headers=json_headers,
        json={"amount": 999999},
    )
    assert resp.status_code == 400


def test_loyalty_redeem_invalid_values_rejected(session, base_url, json_headers):
    zero_resp = api_call(
        session,
        base_url,
        "POST",
        "/loyalty/redeem",
        headers=json_headers,
        json={"points": 0},
    )
    assert zero_resp.status_code == 400

    large_resp = api_call(
        session,
        base_url,
        "POST",
        "/loyalty/redeem",
        headers=json_headers,
        json={"points": 999999},
    )
    assert large_resp.status_code == 400


def test_order_detail_non_existing_returns_404(session, base_url, json_headers):
    resp = api_call(session, base_url, "GET", "/orders/999999", headers=json_headers)
    assert resp.status_code == 404


def test_cancel_delivered_order_rejected(session, base_url, json_headers):
    list_resp = api_call(session, base_url, "GET", "/orders", headers=json_headers)
    assert list_resp.status_code == 200
    delivered = [o for o in list_resp.json() if o["order_status"] == "DELIVERED"]
    if not delivered:
        pytest.skip("No delivered order available for this user")

    order_id = delivered[0]["order_id"]
    resp = api_call(
        session,
        base_url,
        "POST",
        f"/orders/{order_id}/cancel",
        headers=json_headers,
    )
    assert resp.status_code == 400


def test_cancel_non_existing_order_returns_404(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/orders/999999/cancel",
        headers=json_headers,
    )
    assert resp.status_code == 404


def test_cancel_order_restocks_inventory(session, base_url, json_headers, created_order):
    product_id = created_order["product_id"]
    order_id = created_order["order_id"]

    before_cancel_resp = api_call(session, base_url, "GET", f"/products/{product_id}", headers=json_headers)
    assert before_cancel_resp.status_code == 200
    stock_before_cancel = before_cancel_resp.json()["stock_quantity"]

    cancel_resp = api_call(
        session,
        base_url,
        "POST",
        f"/orders/{order_id}/cancel",
        headers=json_headers,
    )
    assert cancel_resp.status_code == 200

    after_cancel_resp = api_call(session, base_url, "GET", f"/products/{product_id}", headers=json_headers)
    assert after_cancel_resp.status_code == 200
    stock_after_cancel = after_cancel_resp.json()["stock_quantity"]

    assert stock_after_cancel == stock_before_cancel + 1


def test_invoice_total_matches_order_total(session, base_url, json_headers, created_order):
    order_id = created_order["order_id"]
    detail_resp = api_call(session, base_url, "GET", f"/orders/{order_id}", headers=json_headers)
    invoice_resp = api_call(session, base_url, "GET", f"/orders/{order_id}/invoice", headers=json_headers)

    assert detail_resp.status_code == 200
    assert invoice_resp.status_code == 200

    detail = detail_resp.json()
    invoice = invoice_resp.json()

    assert float(invoice["subtotal"]) + float(invoice["gst_amount"]) == float(invoice["total_amount"])
    assert float(invoice["total_amount"]) == float(detail["total_amount"])


def test_support_create_subject_and_message_boundaries(session, base_url, json_headers, unique_suffix):
    short_subject_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={"subject": "Hey", "message": "abc"},
    )
    assert short_subject_resp.status_code == 400

    long_message_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={"subject": f"Valid subject {unique_suffix}", "message": "m" * 501},
    )
    assert long_message_resp.status_code == 400


def test_support_message_saved_exactly(session, base_url, json_headers, unique_suffix):
    message = f"Exact message check :: {unique_suffix}"
    create_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={"subject": f"Tracking {unique_suffix}", "message": message},
    )
    assert create_resp.status_code == 200
    ticket_id = str(create_resp.json()["ticket_id"])

    admin_resp = api_call(
        session,
        base_url,
        "GET",
        "/admin/tickets",
        headers={"X-Roll-Number": json_headers["X-Roll-Number"]},
    )
    assert admin_resp.status_code == 200

    created = [t for t in admin_resp.json() if str(t["ticket_id"]) == ticket_id][0]
    assert created["status"] == "OPEN"
    assert created["message"] == message


def test_support_invalid_status_transition_rejected(session, base_url, json_headers, unique_suffix):
    create_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={"subject": f"Transition test {unique_suffix}", "message": "Need status change"},
    )
    assert create_resp.status_code == 200
    ticket_id = create_resp.json()["ticket_id"]

    invalid_resp = api_call(
        session,
        base_url,
        "PUT",
        f"/support/tickets/{ticket_id}",
        headers=json_headers,
        json={"status": "CLOSED"},
    )
    assert invalid_resp.status_code == 400


def test_support_update_non_existing_ticket_returns_404(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "PUT",
        "/support/tickets/999999",
        headers=json_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert resp.status_code == 404
