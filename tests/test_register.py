from database.db import create_user, get_user_by_email


def test_register_success_redirects_to_login(client):
    resp = client.post(
        "/register",
        data={"name": "Alice", "email": "alice@example.com", "password": "supersecret"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    user = get_user_by_email("alice@example.com")
    assert user is not None
    assert user["name"] == "Alice"
    assert user["password_hash"].split(":", 1)[0] in {"scrypt", "pbkdf2"}


def test_register_duplicate_email_renders_error(client):
    create_user("Bob", "bob@example.com", "supersecret")

    resp = client.post(
        "/register",
        data={"name": "Bobby", "email": "bob@example.com", "password": "anothersecret"},
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "already exists" in body

    user = get_user_by_email("bob@example.com")
    assert user["name"] == "Bob"


def test_register_invalid_password_repopulates_name_and_email(client):
    resp = client.post(
        "/register",
        data={"name": "Carol", "email": "carol@example.com", "password": "abc"},
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "at least 8" in body
    assert 'value="Carol"' in body
    assert 'value="carol@example.com"' in body
    assert 'name="password"' in body and 'value="abc"' not in body
    assert get_user_by_email("carol@example.com") is None
