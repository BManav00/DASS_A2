import pytest

from conftest import api_call


@pytest.mark.parametrize(
    "endpoint,required_keys",
    [
        ("/admin/carts", {"cart_id", "user_id", "items", "total"}),
        ("/admin/orders", {"order_id", "user_id", "total_amount", "payment_status", "order_status"}),
        ("/admin/products", {"product_id", "name", "category", "price", "stock_quantity", "is_active"}),
        ("/admin/coupons", {"coupon_code", "discount_type", "discount_value", "min_cart_value", "max_discount", "expiry_date", "is_active"}),
        ("/admin/tickets", {"ticket_id", "user_id", "status", "subject", "message"}),
        ("/admin/addresses", {"address_id", "user_id", "label", "street", "city", "pincode", "is_default"}),
    ],
)
def test_admin_collection_endpoints_success(
    session,
    base_url,
    admin_headers,
    endpoint,
    required_keys,
):
    resp = api_call(session, base_url, "GET", endpoint, headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0
    assert required_keys.issubset(body[0].keys())


def test_admin_users_and_admin_user_by_id_success(session, base_url, admin_headers):
    users_resp = api_call(session, base_url, "GET", "/admin/users", headers=admin_headers)
    assert users_resp.status_code == 200
    users = users_resp.json()
    assert isinstance(users, list)
    assert len(users) > 0

    first_user = users[0]
    assert {"user_id", "name", "email", "phone", "wallet_balance", "loyalty_points"}.issubset(first_user.keys())

    user_resp = api_call(
        session,
        base_url,
        "GET",
        f"/admin/users/{first_user['user_id']}",
        headers=admin_headers,
    )
    assert user_resp.status_code == 200
    assert user_resp.json()["user_id"] == first_user["user_id"]


def test_products_list_success_and_only_active(session, base_url, user_headers):
    resp = api_call(session, base_url, "GET", "/products", headers=user_headers)
    assert resp.status_code == 200
    products = resp.json()
    assert isinstance(products, list)
    assert len(products) > 0
    assert all(p["is_active"] is True for p in products)


def test_product_lookup_by_id_success(session, base_url, user_headers):
    products_resp = api_call(session, base_url, "GET", "/products", headers=user_headers)
    product = products_resp.json()[0]

    detail_resp = api_call(
        session,
        base_url,
        "GET",
        f"/products/{product['product_id']}",
        headers=user_headers,
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["product_id"] == product["product_id"]
    assert detail["price"] == product["price"]


def test_products_filter_search_and_sort_success(session, base_url, user_headers):
    full_resp = api_call(session, base_url, "GET", "/products", headers=user_headers)
    assert full_resp.status_code == 200
    full_list = full_resp.json()
    assert len(full_list) > 0

    sample_category = full_list[0]["category"]
    category_resp = api_call(
        session,
        base_url,
        "GET",
        "/products",
        headers=user_headers,
        params={"category": sample_category},
    )
    assert category_resp.status_code == 200
    category_products = category_resp.json()
    assert all(p["category"] == sample_category for p in category_products)

    sample_name_token = full_list[0]["name"].split()[0]
    search_resp = api_call(
        session,
        base_url,
        "GET",
        "/products",
        headers=user_headers,
        params={"search": sample_name_token},
    )
    assert search_resp.status_code == 200
    search_products = search_resp.json()
    assert all(sample_name_token.lower() in p["name"].lower() for p in search_products)

    asc_resp = api_call(
        session,
        base_url,
        "GET",
        "/products",
        headers=user_headers,
        params={"sort": "price_asc"},
    )
    desc_resp = api_call(
        session,
        base_url,
        "GET",
        "/products",
        headers=user_headers,
        params={"sort": "price_desc"},
    )
    assert asc_resp.status_code == 200
    assert desc_resp.status_code == 200

    asc_prices = [p["price"] for p in asc_resp.json()]
    desc_prices = [p["price"] for p in desc_resp.json()]
    assert asc_prices == sorted(asc_prices)
    assert desc_prices == sorted(desc_prices, reverse=True)


def test_get_product_reviews_success(session, base_url, user_headers):
    resp = api_call(session, base_url, "GET", "/products/1/reviews", headers=user_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "average_rating" in body
    assert "reviews" in body
    assert isinstance(body["reviews"], list)
