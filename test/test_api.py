import json
from app import api


class Testrouting:
    @staticmethod
    def test_get_default(client):
        response = client.get('/api/v1/tasks?id=1')
        assert response.status_code == 200

    @staticmethod
    def test_get_single_mode(client):
        response = client.get('/api/v1/tasks?id=1&mode=single')
        assert response.status_code == 200

    @staticmethod
    def test_get_bad_mode(client):
        response = client.get('/api/v1/tasks?id=1&mode=bad')
        assert response.status_code == 400

    @staticmethod
    def test_get_missing_id(client):
        response = client.get('/api/v1/tasks')
        assert response.status_code == 400

    @staticmethod
    def test_patch_success(client):
        data = {'title': 'Updated Title', 'status': 'HALF'}
        response = client.patch('/api/v1/tasks?id=1', data=json.dumps(data),
                                headers={"Content-Type": "application/json"})
        assert response.status_code == 200

    @staticmethod
    def test_patch_missing_id(client):
        data = {'title': 'Updated Title', 'status': 'HALF'}
        response = client.patch('/api/v1/tasks', data=json.dumps(data),
                                headers={"Content-Type": "application/json"})
        assert response.status_code == 400

    @staticmethod
    def test_delete_success(client):
        response = client.delete('/api/v1/tasks?id=3')
        assert response.status_code == 204

    @staticmethod
    def test_delete_missing_id(client):
        response = client.delete('/api/v1/tasks')
        assert response.status_code == 400

    @staticmethod
    def test_post_success(client):
        data = {'title': 'Updated Title'}
        response = client.post('/api/v1/tasks', data=json.dumps(data),
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 200


class TestPostTask:
    @staticmethod
    def test_success(app_context):
        data = {'title': 'Test Post', 'parent_id': 1}
        response = api.post_task(data)
        result = json.loads(response.data)
        expected = {'data': [{'id': 6, 'title': 'Test Post',
                    'parent_id': 1, 'status': 'EMPTY'}
                             ]}
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_missing_title(app_context):
        data = {'parent_id': 1}
        response = api.post_task(data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Missing title.'}

    @staticmethod
    def test_auto_fill_parent_id(app_context):
        data = {'title': 'Test Post'}
        response = api.post_task(data)
        result = json.loads(response.data)
        expected = {'data': [{'id': 6, 'title': 'Test Post',
                    'parent_id': None, 'status': 'EMPTY'}
                             ]}
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_bad_parent_id(app_context):
        data = {'title': 'Test Post', 'parent_id': 100}
        response = api.post_task(data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Bad parent id.'}


class TestGetTasks:
    @staticmethod
    def test_get_task_tree(app_context):
        response = api.get_task(1, 'tree')
        expected = {'data':
                    [{'Level': 1, 'id': 1, 'title': 'Main_task_1',
                        'parent_id': None, 'status': 'EMPTY'},
                     {'Level': 2, 'id': 3, 'title': 'Sub_task_1',
                        'parent_id': 1, 'status': 'HALF'},

                     ]}
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_get_all(app_context):
        response = api.get_task(None, 'all')
        expected = {'data':
                    [{'Level': 1, 'id': 1, 'title': 'Main_task_1',
                        'parent_id': None, 'status': 'EMPTY'},
                     {'Level': 1, 'id': 2, 'title': 'Main_task_2',
                        'parent_id': None, 'status': 'EMPTY'},
                     {'Level': 2, 'id': 3, 'title': 'Sub_task_1',
                        'parent_id': 1, 'status': 'HALF'},
                     {'Level': 2, 'id': 4, 'title': 'Sub_task_2',
                        'parent_id': 2, 'status': 'EMPTY'},
                     {'Level': 3, 'id': 5, 'title': 'Bottom_task_1',
                        'parent_id': 4, 'status': 'FULL'},
                     ]}
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_get_task_single(app_context):
        response = api.get_task(1, 'single')
        expected = {'data':
                    [{'id': 1, 'title': 'Main_task_1',
                        'parent_id': None, 'status': 'EMPTY'}
                     ]}
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_get_task_bad_mode(app_context):
        response = api.get_task(1, 'bad_type')
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Bad mode.'}

    @staticmethod
    def test_missing_data(app_context):
        response = api.get_task(10, 'single')
        expected = {'data': []}
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected


class TestFilterTasks:
    @staticmethod
    def test_filter_empty(app_context):
        expected = {'data':
                    [{'id': 1, 'title': 'Main_task_1',
                        'parent_id': None, 'status': 'EMPTY'},
                     {'id': 2, 'title': 'Main_task_2',
                        'parent_id': None, 'status': 'EMPTY'},
                     {'id': 4, 'title': 'Sub_task_2',
                        'parent_id': 2, 'status': 'EMPTY'}
                     ]}
        response = api.filter_task(filter='EMPTY')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_filter_half(app_context):
        expected = {'data':
                    [{'id': 3, 'title': 'Sub_task_1',
                        'parent_id': 1, 'status': 'HALF'}
                     ]}
        response = api.filter_task(filter='HALF')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_filter_full(app_context):
        expected = {'data':
                    [{'id': 5, 'title': 'Bottom_task_1',
                        'parent_id': 4, 'status': 'FULL'}
                     ]}
        response = api.filter_task(filter='FULL')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result == expected


class TestPatchTask:
    @staticmethod
    def test_success(app_context):
        patch_data = {'title': 'Updated Title', 'status': 'HALF'}
        response = api.patch_task(1, patch_data)
        result = json.loads(response.data)
        expected = {'data':
                    [{'id': 1, 'title': 'Updated Title',
                        'parent_id': None, 'status': 'HALF'}
                     ]}
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_bad_id(app_context):
        patch_data = {'title': 'Updated Title', 'status': 'HALF'}
        response = api.patch_task(100, patch_data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Id does not exist.'}

    @staticmethod
    def test_bad_status(app_context):
        patch_data = {'title': 'Updated Title', 'status': 'TRASH'}
        response = api.patch_task(1, patch_data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Bad data.'}

    @staticmethod
    def test_bad_parent(app_context):
        patch_data = {'title': 'Updated Title', 'parent_id': 100}
        response = api.patch_task(1, patch_data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'Bad data.'}

    @staticmethod
    def test_all_bad_fields(app_context):
        patch_data = {'id': '100', 'hack': True}
        response = api.patch_task(1, patch_data)
        result = json.loads(response[0].data)
        assert response[1] == 400
        assert result == {'error': 'All bad fields.'}


class TestDeleteTask:

    @staticmethod
    def test_delete_success(app_context):
        response = api.delete_task(100)
        assert response[0] == ''
        assert response[1] == 204

    @staticmethod
    def test_delete_non_exist_data(app_context):
        response = api.delete_task(100)
        assert response[0] == ''
        assert response[1] == 204

    @staticmethod
    def test_integrity_error(app_context):
        response = api.delete_task(1)
        result = json.loads(response[0].data)
        expected = {'error':
                    'Deletion unsucessful. Please delete all child tasks before deletion.'  # noqa
                    }
        assert result == expected
        assert response[1] == 400


class TestShowLineage:
    @staticmethod
    def test_no_parent_id(app_context):
        response = api.show_lineage(1)
        result = json.loads(response.data)
        expected = {'lineage': []}
        assert response.status_code == 200
        assert result == expected

    @staticmethod
    def test_two_level_parent(app_context):
        response = api.show_lineage(5)
        result = json.loads(response.data)
        expected = {'lineage': [{'id': 4, 'title': 'Sub_task_2'},
                                {'id': 2, 'title': 'Main_task_2'}]}
        assert response.status_code == 200
        assert result == expected


class MockRow:
    def __init__(self, **kwargs):
        self._data = kwargs

    def keys(self):
        return self._data.keys()

    def __iter__(self):
        return iter(self._data.values())


class TestRowsToDict:

    @staticmethod
    def test_with_data():
        mock_data = [
            MockRow(**{"id": 1, "name": "Task 1", "status": "EMPTY"}),
            MockRow(**{"id": 2, "name": "Task 2", "status": "HALF"})
        ]

        expected_result = {
            "data": [
                {"id": 1, "name": "Task 1", "status": "EMPTY"},
                {"id": 2, "name": "Task 2", "status": "HALF"}
            ]
        }
        assert api.RowsToDict(mock_data) == expected_result

    @staticmethod
    def test_empty():
        mock_data = []
        expected_result = {'data': []}
        assert api.RowsToDict(mock_data) == expected_result

    @staticmethod
    def test_assign_key():
        mock_data = []
        expected_result = {'mock_key': []}
        assert api.RowsToDict(mock_data, 'mock_key') == expected_result
