import pytest


@pytest.fixture()
def task(client, auth_headers, project):
    resp = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Test Task"},
        headers=auth_headers,
    )
    return resp.get_json()


class TestGetTasks:
    def test_returns_empty_list(self, client, auth_headers, project):
        resp = client.get(f"/api/projects/{project['id']}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_project_tasks(self, client, auth_headers, project, task):
        resp = client.get(f"/api/projects/{project['id']}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    def test_non_member_returns_404(self, client, second_auth_headers, project):
        resp = client.get(
            f"/api/projects/{project['id']}/tasks", headers=second_auth_headers
        )
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.get(f"/api/projects/{project['id']}/tasks")
        assert resp.status_code == 401


class TestGetTask:
    def test_success(self, client, auth_headers, project, task):
        resp = client.get(
            f"/api/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.get_json()["id"] == task["id"]

    def test_nonexistent_task_returns_404(self, client, auth_headers, project):
        resp = client.get(
            f"/api/projects/{project['id']}/tasks/nonexistent-id", headers=auth_headers
        )
        assert resp.status_code == 404


class TestCreateTask:
    def test_success_with_defaults(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Fix bug"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Fix bug"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["due_date"] is None

    def test_success_with_all_fields(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={
                "title": "Full Task",
                "description": "A task with everything",
                "status": "in_progress",
                "priority": "high",
                "due_date": "2026-12-31",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"
        assert data["due_date"] is not None

    def test_invalid_due_date(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Task", "due_date": "not-a-date"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_invalid_status(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Task", "status": "invalid"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_missing_title(self, client, auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks", json={}, headers=auth_headers
        )
        assert resp.status_code == 422

    def test_non_member_returns_404(self, client, second_auth_headers, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Task"},
            headers=second_auth_headers,
        )
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.post(
            f"/api/projects/{project['id']}/tasks", json={"title": "Task"}
        )
        assert resp.status_code == 401


class TestUpdateTask:
    def test_success(self, client, auth_headers, project, task):
        resp = client.patch(
            f"/api/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "in_progress"

    def test_partial_update_keeps_other_fields(
        self, client, auth_headers, project, task
    ):
        resp = client.patch(
            f"/api/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "done"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert data["title"] == "Test Task"
        assert data["status"] == "done"

    def test_clear_due_date(self, client, auth_headers, project):
        create_resp = client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Task", "due_date": "2026-12-31"},
            headers=auth_headers,
        )
        task_id = create_resp.get_json()["id"]
        resp = client.patch(
            f"/api/projects/{project['id']}/tasks/{task_id}",
            json={"due_date": None},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["due_date"] is None

    def test_nonexistent_task_returns_404(self, client, auth_headers, project):
        resp = client.patch(
            f"/api/projects/{project['id']}/tasks/nonexistent-id",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeleteTask:
    def test_success(self, client, auth_headers, project, task):
        resp = client.delete(
            f"/api/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers
        )
        assert resp.status_code == 200
        resp2 = client.get(
            f"/api/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers
        )
        assert resp2.status_code == 404

    def test_nonexistent_task_returns_404(self, client, auth_headers, project):
        resp = client.delete(
            f"/api/projects/{project['id']}/tasks/nonexistent-id", headers=auth_headers
        )
        assert resp.status_code == 404
