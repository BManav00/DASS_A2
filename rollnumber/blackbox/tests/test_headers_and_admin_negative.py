from conftest import api_call


def test_missing_roll_header_returns_401(session, base_url):
    resp = session.get(f"{base_url}/admin/users", timeout=10)
    assert resp.status_code == 401


def test_invalid_roll_header_returns_400(session, base_url):
    resp = session.get(
        f"{base_url}/admin/users",
        headers={"X-Roll-Number": "abc"},
        timeout=10,
    )
    assert resp.status_code == 400


def test_missing_user_header_returns_400(session, base_url, admin_headers):
    resp = api_call(session, base_url, "GET", "/profile", headers=admin_headers)
    assert resp.status_code == 400


def test_invalid_user_header_returns_400(session, base_url, admin_headers):
    headers = {**admin_headers, "X-User-ID": "invalid"}
    resp = api_call(session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code == 400


def test_non_existing_user_header_returns_400(session, base_url, admin_headers):
    headers = {**admin_headers, "X-User-ID": "999999"}
    resp = api_call(session, base_url, "GET", "/profile", headers=headers)
    assert resp.status_code == 400


def test_admin_user_by_id_not_found_returns_404(session, base_url, admin_headers):
    resp = api_call(session, base_url, "GET", "/admin/users/999999", headers=admin_headers)
    assert resp.status_code == 404
