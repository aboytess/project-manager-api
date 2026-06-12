class TestGetMembers:
    def test_returns_owner_on_creation(
        self, client, auth_headers, registered_user, project
    ):
        resp = client.get(
            f"/api/projects/{project['id']}/members", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["role"] == "owner"
        assert data[0]["user_id"] == registered_user["user"]["id"]

    def test_non_member_returns_404(self, client, second_auth_headers, project):
        resp = client.get(
            f"/api/projects/{project['id']}/members", headers=second_auth_headers
        )
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.get(f"/api/projects/{project['id']}/members")
        assert resp.status_code == 401


class TestAddMember:
    def test_success(self, client, auth_headers, second_user, project):
        resp = client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["role"] == "member"

    def test_new_member_can_access_project(
        self, client, auth_headers, second_auth_headers, second_user, project
    ):
        client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        resp = client.get(f"/api/projects/{project['id']}", headers=second_auth_headers)
        assert resp.status_code == 200

    def test_duplicate_member_returns_409(
        self, client, auth_headers, second_user, project
    ):
        client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        resp = client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    def test_nonexistent_user_returns_404(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": "nonexistent-id"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_non_member_cannot_add(
        self, client, second_auth_headers, second_user, project
    ):
        resp = client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=second_auth_headers,
        )
        assert resp.status_code == 404


class TestUpdateMemberRole:
    def test_owner_can_promote_to_admin(
        self, client, auth_headers, second_user, project
    ):
        client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        resp = client.patch(
            f"/api/projects/{project['id']}/members/{second_user['user']['id']}",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["role"] == "admin"

    def test_cannot_change_owner_role(
        self, client, auth_headers, registered_user, project
    ):
        owner_id = registered_user["user"]["id"]
        resp = client.patch(
            f"/api/projects/{project['id']}/members/{owner_id}",
            json={"role": "member"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_invalid_role_returns_422(self, client, auth_headers, second_user, project):
        client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        resp = client.patch(
            f"/api/projects/{project['id']}/members/{second_user['user']['id']}",
            json={"role": "superuser"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_nonexistent_member_returns_404(
        self, client, auth_headers, second_user, project
    ):
        resp = client.patch(
            f"/api/projects/{project['id']}/members/{second_user['user']['id']}",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestRemoveMember:
    def test_success(
        self, client, auth_headers, second_auth_headers, second_user, project
    ):
        client.post(
            f"/api/projects/{project['id']}/members",
            json={"user_id": second_user["user"]["id"]},
            headers=auth_headers,
        )
        resp = client.delete(
            f"/api/projects/{project['id']}/members/{second_user['user']['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        resp2 = client.get(
            f"/api/projects/{project['id']}", headers=second_auth_headers
        )
        assert resp2.status_code == 404

    def test_cannot_remove_owner(self, client, auth_headers, registered_user, project):
        owner_id = registered_user["user"]["id"]
        resp = client.delete(
            f"/api/projects/{project['id']}/members/{owner_id}", headers=auth_headers
        )
        assert resp.status_code == 400

    def test_non_member_cannot_remove(
        self, client, second_auth_headers, project, registered_user
    ):
        owner_id = registered_user["user"]["id"]
        resp = client.delete(
            f"/api/projects/{project['id']}/members/{owner_id}",
            headers=second_auth_headers,
        )
        assert resp.status_code == 404
