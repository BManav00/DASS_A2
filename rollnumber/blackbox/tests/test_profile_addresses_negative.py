from conftest import api_call


def test_profile_name_boundaries_accept_2_and_50_chars(
    session,
    base_url,
    user_headers,
    profile_snapshot,
):
    headers = {**user_headers, "Content-Type": "application/json"}

    min_name = "Ab"
    max_name = "N" * 50

    min_resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": min_name, "phone": "9876543210"},
    )
    assert min_resp.status_code == 200

    max_resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": max_name, "phone": "9876543210"},
    )
    assert max_resp.status_code == 200


def test_profile_name_too_short_rejected(session, base_url, user_headers):
    headers = {**user_headers, "Content-Type": "application/json"}
    resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": "A", "phone": "9876543210"},
    )
    assert resp.status_code == 400


def test_profile_phone_invalid_and_missing_rejected(session, base_url, user_headers):
    headers = {**user_headers, "Content-Type": "application/json"}

    short_resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": "Valid Name", "phone": "12345"},
    )
    assert short_resp.status_code == 400

    missing_resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": "Valid Name"},
    )
    assert missing_resp.status_code == 400


def test_profile_wrong_phone_type_rejected(session, base_url, user_headers):
    headers = {**user_headers, "Content-Type": "application/json"}
    resp = api_call(
        session,
        base_url,
        "PUT",
        "/profile",
        headers=headers,
        json={"name": "Valid Name", "phone": 1234567890},
    )
    assert resp.status_code == 400


def test_address_create_invalid_label_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json={
            "label": "WORK",
            "street": "12345 MG Road",
            "city": "Pune",
            "pincode": "411001",
            "is_default": False,
        },
    )
    assert resp.status_code == 400


def test_address_missing_field_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json={"label": "HOME", "street": "12345 MG Road", "city": "Pune", "is_default": False},
    )
    assert resp.status_code == 400


def test_address_wrong_pincode_type_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        data='{"label":"HOME","street":"12345 MG Road","city":"Pune","pincode":411001,"is_default":false}',
    )
    assert resp.status_code == 400


def test_address_boundary_values_accept_valid_limits(session, base_url, json_headers, unique_suffix):
    min_payload = {
        "label": "OTHER",
        "street": "A" * 5,
        "city": "AB",
        "pincode": "123456",
        "is_default": False,
    }
    min_resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json=min_payload,
    )
    assert min_resp.status_code == 200
    min_id = min_resp.json()["address"]["address_id"]

    max_payload = {
        "label": "OFFICE",
        "street": "B" * 100,
        "city": "C" * 50,
        "pincode": "654321",
        "is_default": False,
    }
    max_resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json=max_payload,
    )
    assert max_resp.status_code == 200
    max_id = max_resp.json()["address"]["address_id"]

    api_call(session, base_url, "DELETE", f"/addresses/{min_id}", headers=json_headers)
    api_call(session, base_url, "DELETE", f"/addresses/{max_id}", headers=json_headers)


def test_address_update_must_return_and_persist_updated_data(
    session,
    base_url,
    json_headers,
    temp_address,
    unique_suffix,
):
    new_street = f"99999 Updated Street {unique_suffix}"
    update_resp = api_call(
        session,
        base_url,
        "PUT",
        f"/addresses/{temp_address['address_id']}",
        headers=json_headers,
        json={"street": new_street, "is_default": True},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()["address"]
    assert updated["street"] == new_street
    assert updated["is_default"] is True

    list_resp = api_call(session, base_url, "GET", "/addresses", headers=json_headers)
    assert list_resp.status_code == 200
    latest = [a for a in list_resp.json() if a["address_id"] == temp_address["address_id"]][0]
    assert latest["street"] == new_street
    assert latest["is_default"] is True


def test_address_delete_non_existing_returns_404(session, base_url, json_headers):
    resp = api_call(session, base_url, "DELETE", "/addresses/999999", headers=json_headers)
    assert resp.status_code == 404
