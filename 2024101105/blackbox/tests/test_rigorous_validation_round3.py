import math

from conftest import api_call


def test_cart_add_requires_quantity_field(session, base_url, json_headers, cart_clean):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1},
    )
    assert resp.status_code == 400


def test_cart_update_requires_product_id_field(session, base_url, json_headers, cart_clean):
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
        json={"quantity": 2},
    )
    assert resp.status_code == 400


def test_get_reviews_for_nonexistent_product_returns_404(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "GET",
        "/products/987654321/reviews",
        headers=json_headers,
    )
    assert resp.status_code == 404


def test_coupon_percent_discount_respects_max_cap(session, base_url, json_headers, cart_clean):
    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 50},
    )
    assert add_resp.status_code == 200

    apply_resp = api_call(
        session,
        base_url,
        "POST",
        "/coupon/apply",
        headers=json_headers,
        json={"coupon_code": "PERCENT30"},
    )
    assert apply_resp.status_code == 200
    body = apply_resp.json()
    assert body["discount"] == 300


def test_coupon_fixed_discount_applies_exact_value(session, base_url, json_headers, cart_clean):
    add_resp = api_call(
        session,
        base_url,
        "POST",
        "/cart/add",
        headers=json_headers,
        json={"product_id": 1, "quantity": 5},
    )
    assert add_resp.status_code == 200

    apply_resp = api_call(
        session,
        base_url,
        "POST",
        "/coupon/apply",
        headers=json_headers,
        json={"coupon_code": "SAVE50"},
    )
    assert apply_resp.status_code == 200
    body = apply_resp.json()
    assert body["discount"] == 50


def test_address_default_uniqueness_after_adding_new_default(
    session,
    base_url,
    json_headers,
    unique_suffix,
):
    first_resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json={
            "label": "HOME",
            "street": f"55555 First Default {unique_suffix}",
            "city": "Pune",
            "pincode": "411005",
            "is_default": True,
        },
    )
    assert first_resp.status_code == 200
    first_id = first_resp.json()["address"]["address_id"]

    second_resp = api_call(
        session,
        base_url,
        "POST",
        "/addresses",
        headers=json_headers,
        json={
            "label": "OFFICE",
            "street": f"66666 Second Default {unique_suffix}",
            "city": "Pune",
            "pincode": "411006",
            "is_default": True,
        },
    )
    assert second_resp.status_code == 200
    second_id = second_resp.json()["address"]["address_id"]

    list_resp = api_call(session, base_url, "GET", "/addresses", headers=json_headers)
    assert list_resp.status_code == 200
    defaults = [a for a in list_resp.json() if a["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["address_id"] == second_id

    api_call(session, base_url, "DELETE", f"/addresses/{first_id}", headers=json_headers)
    api_call(session, base_url, "DELETE", f"/addresses/{second_id}", headers=json_headers)


def test_review_average_uses_exact_decimal_math(session, base_url, json_headers, unique_suffix):
    product_id = 2
    before_resp = api_call(
        session,
        base_url,
        "GET",
        f"/products/{product_id}/reviews",
        headers=json_headers,
    )
    assert before_resp.status_code == 200
    before = before_resp.json()
    prev_reviews = before["reviews"]
    prev_sum = sum(r["rating"] for r in prev_reviews)
    prev_count = len(prev_reviews)

    add_a = api_call(
        session,
        base_url,
        "POST",
        f"/products/{product_id}/reviews",
        headers=json_headers,
        json={"rating": 2, "comment": f"decimal check a {unique_suffix}"},
    )
    add_b = api_call(
        session,
        base_url,
        "POST",
        f"/products/{product_id}/reviews",
        headers=json_headers,
        json={"rating": 5, "comment": f"decimal check b {unique_suffix}"},
    )
    assert add_a.status_code == 200
    assert add_b.status_code == 200

    after_resp = api_call(
        session,
        base_url,
        "GET",
        f"/products/{product_id}/reviews",
        headers=json_headers,
    )
    assert after_resp.status_code == 200
    observed_avg = float(after_resp.json()["average_rating"])

    expected_avg = (prev_sum + 2 + 5) / (prev_count + 2)
    assert math.isclose(observed_avg, expected_avg, rel_tol=0, abs_tol=1e-9)
