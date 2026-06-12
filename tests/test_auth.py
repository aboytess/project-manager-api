class TestRegister:
    def test_success(self, client):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "new@example.com"

    def test_duplicate_email(self, client, registered_user):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "different",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 409

    def test_duplicate_username(self, client, registered_user):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 409

    def test_short_password(self, client):
        resp = client.post(
            "/api/auth/register",
            json={"username": "user", "email": "user@example.com", "password": "short"},
        )
        assert resp.status_code == 422

    def test_missing_field(self, client):
        resp = client.post(
            "/api/auth/register", json={"username": "user", "email": "user@example.com"}
        )
        assert resp.status_code == 422


class TestLogin:
    def test_success(self, client, registered_user):
        resp = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.get_json()

    def test_wrong_password(self, client, registered_user):
        resp = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_unknown_email(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert resp.status_code == 401


class TestLogout:
    def test_success(self, client, auth_headers):
        resp = client.delete("/api/auth/logout", headers=auth_headers)
        assert resp.status_code == 200

    def test_token_is_revoked_after_logout(self, client, auth_headers):
        client.delete("/api/auth/logout", headers=auth_headers)
        resp = client.get("/api/projects", headers=auth_headers)
        assert resp.status_code == 401

    def test_no_token(self, client):
        resp = client.delete("/api/auth/logout")
        assert resp.status_code == 401


class TestRefresh:
    def test_success(self, client, registered_user):
        headers = {"Authorization": f"Bearer {registered_user['refresh_token']}"}
        resp = client.post("/api/auth/refresh", headers=headers)
        assert resp.status_code == 200
        assert "access_token" in resp.get_json()

    def test_access_token_rejected(self, client, auth_headers):
        resp = client.post("/api/auth/refresh", headers=auth_headers)
        assert resp.status_code == 401
