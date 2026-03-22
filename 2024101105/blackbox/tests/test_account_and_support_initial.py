from conftest import api_call


def test_get_and_update_profile_success(session, base_url, user_headers, profile_snapshot):
    get_resp = api_call(session, base_url, "GET", "/profile", headers=user_headers)
    assert get_resp.status_code == 200
    before = get_resp.json()

    update_payload = {
        "name": "QA Smoke",
        "phone": "9876543210",
    }
    put_resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers={**user_headers, "Content-Type": "application/json"},
        json=update_payload,
    )
    assert put_resp.status_code == 200
    assert "message" in put_resp.json()

    after_resp = api_call(session, base_url, "GET", "/profile", headers=user_headers)
    assert after_resp.status_code == 200
    after = after_resp.json()
    assert after["user_id"] == before["user_id"]


def test_addresses_crud_smoke(session, base_url, json_headers, unique_suffix):
    list_resp = api_call(session, base_url, "GET", "/addresses", headers=json_headers)
    assert list_resp.status_code == 200
    assert isinstance(list_resp.json(), list)

    create_payload = {
        "label": "HOME",
        "street": f"12345 QA Street {unique_suffix}",
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
        json=create_payload,
    )
    assert create_resp.status_code == 200
    created = create_resp.json()["address"]

    update_resp = api_call(
        session,
        base_url,
        "PUT",
        f"/addresses/{created['address_id']}",
        headers=json_headers,
        json={"street": f"54321 QA Street {unique_suffix}", "is_default": False},
    )
    assert update_resp.status_code == 200

    delete_resp = api_call(
        session,
        base_url,
        "DELETE",
        f"/addresses/{created['address_id']}",
        headers=json_headers,
    )
    assert delete_resp.status_code == 200


def test_wallet_endpoints_success(session, base_url, json_headers):
    wallet_resp = api_call(session, base_url, "GET", "/wallet", headers=json_headers)
    assert wallet_resp.status_code == 200
    assert "wallet_balance" in wallet_resp.json()

    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/add",
        headers=json_headers,
        json={"amount": 1},
    )
    assert add_resp.status_code == 200
    assert "wallet_balance" in add_resp.json()

    pay_resp = api_call(
        session,
        base_url,
        "POST",
        "/wallet/pay",
        headers=json_headers,
        json={"amount": 1},
    )
    assert pay_resp.status_code == 200
    assert "wallet_balance" in pay_resp.json()


def test_loyalty_endpoints_success(session, base_url, json_headers):
    loyalty_resp = api_call(session, base_url, "GET", "/loyalty", headers=json_headers)
    assert loyalty_resp.status_code == 200
    before = loyalty_resp.json()["loyalty_points"]

    redeem_resp = api_call(
        session,
        base_url,
        "POST",
        "/loyalty/redeem",
        headers=json_headers,
        json={"points": 1},
    )
    assert redeem_resp.status_code == 200
    after = redeem_resp.json()["loyalty_points"]
    assert after == before - 1


def test_support_ticket_flow_success(session, base_url, json_headers, unique_suffix):
    create_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={
            "subject": f"Refund followup {unique_suffix}",
            "message": "Need update for refund request",
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["status"] == "OPEN"

    tickets_resp = api_call(session, base_url, "GET", "/support/tickets", headers=json_headers)
    assert tickets_resp.status_code == 200
    tickets = tickets_resp.json()
    assert any(str(t["ticket_id"]) == str(created["ticket_id"]) for t in tickets)

    in_progress_resp = api_call(
        session,
        base_url,
        "PUT",
        f"/support/tickets/{created['ticket_id']}",
        headers=json_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert in_progress_resp.status_code == 200
    assert in_progress_resp.json()["status"] == "IN_PROGRESS"

    close_resp = api_call(
        session,
        base_url,
        "PUT",
        f"/support/tickets/{created['ticket_id']}",
        headers=json_headers,
        json={"status": "CLOSED"},
    )
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "CLOSED"
