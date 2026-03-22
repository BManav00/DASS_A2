import uuid

from conftest import api_call


def test_review_post_for_nonexistent_product_is_rejected(session, base_url, json_headers):
    missing_product_id = 900000 + int(uuid.uuid4().hex[:5], 16)
    review_resp = api_call(
        session,
        base_url,
        "POST",
        f"/products/{missing_product_id}/reviews",
        headers=json_headers,
        json={"rating": 5, "comment": "should not be accepted"},
    )
    assert review_resp.status_code == 404


def test_support_ticket_list_contains_saved_message_for_user_view(
    session,
    base_url,
    json_headers,
    unique_suffix,
):
    expected_message = f"User-visible message check {unique_suffix}"
    create_resp = api_call(
        session,
        base_url,
        "POST",
        "/support/ticket",
        headers=json_headers,
        json={
            "subject": f"Visibility {unique_suffix}",
            "message": expected_message,
        },
    )
    assert create_resp.status_code == 200
    ticket_id = str(create_resp.json()["ticket_id"])

    list_resp = api_call(session, base_url, "GET", "/support/tickets", headers=json_headers)
    assert list_resp.status_code == 200
    tickets = list_resp.json()

    created = [t for t in tickets if str(t["ticket_id"]) == ticket_id][0]
    assert "message" in created
    assert created["message"] == expected_message
