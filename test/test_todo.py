from app import todo
import pytest


def test_cleanup_task():
    task = {'Level': 1, 'id': 1, 'title': 'Main_task_1',
            'parent_id': None, 'status': 'EMPTY'}
    result = todo.cleanup_task(task)
    expected = {'id': 1, 'title': 'Main_task_1',
                'status': 'EMPTY'}
    assert result == expected


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


def test_tasks_to_trees(tasks):

    trees = todo.tasks_to_trees(tasks)
    expected = [
        {'id': 1, 'title': 'Main_task_1', 'status': 'EMPTY',
            'sub_tasks': [
                {'id': 3, 'title': 'Sub_task_1', 'status': 'HALF'}
            ]},
        {'id': 2, 'title': 'Main_task_2', 'status': 'EMPTY',
            'sub_tasks': [
                {'id': 4, 'title': 'Sub_task_2', 'status': 'EMPTY',
                 'sub_tasks': [
                     {'id': 5, 'title': 'Bottom_task_1', 'status': 'FULL'}
                 ]}
            ]}]
    assert trees == expected
