class TestGetProjects:
    def test_returns_empty_list_when_no_projects(self, client, auth_headers):
        resp = client.get('/api/projects', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_own_projects(self, client, auth_headers, project):
        resp = client.get('/api/projects', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Test Project'

    def test_does_not_return_other_users_projects(self, client, second_auth_headers, project):
        resp = client.get('/api/projects', headers=second_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_no_token(self, client):
        resp = client.get('/api/projects')
        assert resp.status_code == 401


class TestGetProject:
    def test_success(self, client, auth_headers, project):
        resp = client.get(f'/api/projects/{project["id"]}', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['id'] == project['id']

    def test_not_member_returns_404(self, client, second_auth_headers, project):
        resp = client.get(f'/api/projects/{project["id"]}', headers=second_auth_headers)
        assert resp.status_code == 404

    def test_nonexistent_project_returns_404(self, client, auth_headers):
        resp = client.get('/api/projects/nonexistent-id', headers=auth_headers)
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.get(f'/api/projects/{project["id"]}')
        assert resp.status_code == 401


class TestCreateProject:
    def test_success(self, client, auth_headers):
        resp = client.post('/api/projects', json={'name': 'New Project'}, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'New Project'
        assert 'id' in data
        assert 'owner_id' in data

    def test_creator_is_added_as_owner(self, client, auth_headers, registered_user):
        resp = client.post('/api/projects', json={'name': 'New Project'}, headers=auth_headers)
        project_id = resp.get_json()['id']
        members_resp = client.get(f'/api/projects/{project_id}/members', headers=auth_headers)
        members = members_resp.get_json()
        assert len(members) == 1
        assert members[0]['role'] == 'owner'
        assert members[0]['user_id'] == registered_user['user']['id']

    def test_missing_name(self, client, auth_headers):
        resp = client.post('/api/projects', json={}, headers=auth_headers)
        assert resp.status_code == 422

    def test_no_token(self, client):
        resp = client.post('/api/projects', json={'name': 'New Project'})
        assert resp.status_code == 401


class TestUpdateProject:
    def test_success(self, client, auth_headers, project):
        resp = client.patch(f'/api/projects/{project["id"]}',
                            json={'name': 'Updated Name'}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Updated Name'

    def test_partial_update_keeps_other_fields(self, client, auth_headers, project):
        resp = client.patch(f'/api/projects/{project["id"]}',
                            json={'name': 'New Name'}, headers=auth_headers)
        assert resp.get_json()['description'] == 'A test project'

    def test_non_member_returns_404(self, client, second_auth_headers, project):
        resp = client.patch(f'/api/projects/{project["id"]}',
                            json={'name': 'Hack'}, headers=second_auth_headers)
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.patch(f'/api/projects/{project["id"]}', json={'name': 'x'})
        assert resp.status_code == 401


class TestDeleteProject:
    def test_success(self, client, auth_headers, project):
        resp = client.delete(f'/api/projects/{project["id"]}', headers=auth_headers)
        assert resp.status_code == 200
        resp2 = client.get(f'/api/projects/{project["id"]}', headers=auth_headers)
        assert resp2.status_code == 404

    def test_non_member_returns_404(self, client, second_auth_headers, project):
        resp = client.delete(f'/api/projects/{project["id"]}', headers=second_auth_headers)
        assert resp.status_code == 404

    def test_no_token(self, client, project):
        resp = client.delete(f'/api/projects/{project["id"]}')
        assert resp.status_code == 401
