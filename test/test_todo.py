from app.flask_app import todo
import pytest
import json


@pytest.fixture
def tasks():
    tasks = [{'Level': 1, 'id': 1, 'title': 'Main_task_1',
              'parent_id': None, 'status': 'EMPTY'},
             {'Level': 1, 'id': 2, 'title': 'Main_task_2',
              'parent_id': None, 'status': 'EMPTY'},
             {'Level': 2, 'id': 3, 'title': 'Sub_task_1',
                          'parent_id': 1, 'status': 'HALF'},
             {'Level': 2, 'id': 4, 'title': 'Sub_task_2',
                          'parent_id': 2, 'status': 'EMPTY'},
             {'Level': 3, 'id': 5, 'title': 'Bottom_task_1',
                          'parent_id': 4, 'status': 'FULL'},
             ]
    return tasks


class TestRouting:
    @staticmethod
    def test_home(client, monkeypatch):
        monkeypatch.setattr('app.src.todo.render_template',
                            lambda file, tasks, parents: file)
        response = client.get('/')
        assert response.status_code == 200
        assert response.data == b'index.html'

    @staticmethod
    def test_single_task(client, monkeypatch):
        monkeypatch.setattr('app.src.todo.render_template',
                            lambda file, main_task, tasks,
                            edit_parents, new_parents: file)
        response = client.get('/1')
        assert response.status_code == 200
        assert response.data == b'single_task.html'

    @staticmethod
    def test_single_task_204(client):
        response = client.get('/100')
        assert response.status_code == 204


@pytest.fixture
def replace_func_for_filter(monkeypatch):
    monkeypatch.setattr('app.src.api.filter_task',
                        lambda filter: ({'tasks': [{'id': 1, 'mode': filter}]},
                                        200))
    monkeypatch.setattr('app.src.api.get_task',
                        lambda id, mode: ({'tasks': [{'id': 1, 'mode': mode}]},
                                          200))
    monkeypatch.setattr('app.src.api.show_lineage',
                        lambda id: ({}, 200))
    monkeypatch.setattr('app.src.todo.render_template',
                        lambda file, tasks: {'file': file, 'data': tasks})


class TestFilter:
    @staticmethod
    def test_filter_ongoing(replace_func_for_filter, client):
        response = client.get('/filter?mode=ongoing')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result['file'] == 'filter.html'
        assert result['data'] == [{'id': 1, 'mode': 'HALF'}]

    @staticmethod
    def test_filter_pending(replace_func_for_filter, client):
        response = client.get('/filter?mode=pending')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result['file'] == 'filter.html'
        assert result['data'] == [{'id': 1, 'mode': 'EMPTY'}]

    @staticmethod
    def test_filter_completed(replace_func_for_filter, client):
        response = client.get('/filter?mode=completed')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result['file'] == 'filter.html'
        assert result['data'] == [{'id': 1, 'mode': 'FULL'}]

    @staticmethod
    def test_filter_bad_mode(replace_func_for_filter, client):
        response = client.get('/filter?mode=none')
        result = json.loads(response.data)
        assert response.status_code == 200
        assert result['file'] == 'filter.html'
        assert result['data'] == [{'id': 1, 'mode': 'all'}]


@pytest.fixture
def submit_data():
    return {
        'id': 2,
        'parent_id': 1
    }


class TestSubmit:
    @staticmethod
    def test_delete_default_header(client, submit_data, monkeypatch):
        monkeypatch.setattr('app.src.todo.redirect', lambda url: url)
        response = client.post('/submit?process=delete', data=submit_data)
        assert response.status_code == 200
        assert response.data == b'/'

    @staticmethod
    def test_delete_with_header(client, submit_data, monkeypatch):
        monkeypatch.setattr('app.src.todo.redirect', lambda url: url)
        response = client.post('/submit?process=delete', data=submit_data,
                               headers={"Referer": '/100'})
        assert response.status_code == 200
        assert response.data == b'/100'

    @staticmethod
    def test_edit(client, submit_data, monkeypatch):
        monkeypatch.setattr('app.src.todo.redirect', lambda url: url)
        response = client.post('/submit?process=edit', data=submit_data)
        assert response.status_code == 200
        assert response.data == b'/1'

    @staticmethod
    def test_edit_parent_id_none(client, submit_data, monkeypatch):
        submit_data['parent_id'] = ''
        monkeypatch.setattr('app.src.todo.redirect', lambda url: url)
        response = client.post('/submit?process=edit', data=submit_data)
        assert response.status_code == 200
        assert response.data == b'/'

    @staticmethod
    def test_unknown_process(client, submit_data):
        response = client.post('/submit?process=unknown', data=submit_data)
        response.status_code == 404
        response.data = b'Process not known'


def test_tasks_to_trees(tasks):

    trees = todo.tasks_to_trees(tasks)
    expected = [
        {'Level': 1, 'id': 1, 'title': 'Main_task_1',
         'status': 'EMPTY', 'parent_id': None,
         'sub_tasks': [
             {'Level': 2, 'id': 3, 'title': 'Sub_task_1',
              'status': 'HALF', 'parent_id': 1}
         ]},
        {'Level': 1, 'id': 2, 'title': 'Main_task_2',
         'status': 'EMPTY', 'parent_id': None,
         'sub_tasks': [
             {'Level': 2, 'id': 4, 'title': 'Sub_task_2',
              'status': 'EMPTY', 'parent_id': 2,
              'sub_tasks': [
                  {'Level': 3, 'id': 5, 'title': 'Bottom_task_1',
                   'status': 'FULL', 'parent_id': 4}
              ]}
         ]}]
    assert trees == expected


def test_list_parent_options(tasks):
    result = todo.list_parent_options(tasks)
    expected = [{'id': 1, 'title': 'Main_task_1'},
                {'id': 2, 'title': 'Main_task_2'},
                {'id': 3, 'title': 'Sub_task_1'},
                {'id': 4, 'title': 'Sub_task_2'},
                {'id': 5, 'title': 'Bottom_task_1'}
                ]
    assert result == expected
