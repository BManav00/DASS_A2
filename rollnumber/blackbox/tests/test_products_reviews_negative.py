from conftest import api_call


def test_product_not_found_returns_404(session, base_url, user_headers):
    resp = api_call(session, base_url, "GET", "/products/999999", headers=user_headers)
    assert resp.status_code == 404


def test_product_prices_match_admin_source(session, base_url, user_headers, admin_headers):
    user_list_resp = api_call(session, base_url, "GET", "/products", headers=user_headers)
    admin_list_resp = api_call(session, base_url, "GET", "/admin/products", headers=admin_headers)

    assert user_list_resp.status_code == 200
    assert admin_list_resp.status_code == 200

    user_products = user_list_resp.json()
    admin_products = {p["product_id"]: p for p in admin_list_resp.json()}

    for product in user_products[:25]:
        admin_price = admin_products[product["product_id"]]["price"]
        assert product["price"] == admin_price


def test_reviews_average_is_decimal_when_fractional(session, base_url, json_headers, unique_suffix):
    create_a = api_call(
        session,
        base_url,
        "POST",
        "/products/2/reviews",
        headers=json_headers,
        json={"rating": 4, "comment": f"avg check A {unique_suffix}"},
    )
    create_b = api_call(
        session,
        base_url,
        "POST",
        "/products/2/reviews",
        headers=json_headers,
        json={"rating": 5, "comment": f"avg check B {unique_suffix}"},
    )
    assert create_a.status_code == 200
    assert create_b.status_code == 200

    get_resp = api_call(session, base_url, "GET", "/products/2/reviews", headers=json_headers)
    assert get_resp.status_code == 200
    avg = get_resp.json()["average_rating"]
    assert isinstance(avg, (int, float))
    assert float(avg) >= 0


def test_review_rating_below_range_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 0, "comment": "below range"},
    )
    assert resp.status_code == 400


def test_review_rating_above_range_rejected(session, base_url, json_headers):
    resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 6, "comment": "above range"},
    )
    assert resp.status_code == 400


def test_review_comment_boundaries(session, base_url, json_headers):
    one_char_resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 3, "comment": "a"},
    )
    assert one_char_resp.status_code == 200

    two_hundred_char_resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 3, "comment": "b" * 200},
    )
    assert two_hundred_char_resp.status_code == 200

    empty_resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 3, "comment": ""},
    )
    assert empty_resp.status_code == 400

    too_long_resp = api_call(
        session,
        base_url,
        "POST",
        "/products/1/reviews",
        headers=json_headers,
        json={"rating": 3, "comment": "c" * 201},
    )
    assert too_long_resp.status_code == 400
