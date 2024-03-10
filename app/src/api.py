from flask import (
    Blueprint, request, redirect, Response, flash)
from .db import get_db
from sqlite3 import Row
from typing import Literal
from .utils import build_response


bp = Blueprint('api', __name__, url_prefix="/api/v1")


@bp.route('/tasks', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def task_by_id() -> Response:
    '''
    Description
    -----------
    Methods allowed: ['GET', 'POST', 'PATCH', 'DELETE'].

    POST method can accept data from request data or html form.

    Accept url params
    ---------------
    id: int
    mode: ['tree', 'single', 'all'] (Only used in GET)
    filter: status options in db ['empty', 'half', 'full'] (Only used in GET)
    '''
    id = request.args.get('id', default=None, type=int)
    mode = request.args.get('mode', default='', type=str).lower()
    filter = request.args.get('filter', default='', type=str).lower()

    if id is not None:
        if request.method == 'GET':
            if mode == '':
                mode = 'tree'
            result, status_code = get_task(id, mode)
            return build_response(result, status_code)

        if request.method == 'PATCH':
            data = request.json
            result, status_code = patch_task(id, data)
            return build_response(result, status_code)

        elif request.method == 'DELETE':
            result, status_code = delete_task(id)
            return build_response(result, status_code)

    if request.method == 'GET':
        result, status_code = filter_task(filter)
        return build_response(result, status_code)

    elif request.method == 'POST':
        '''
        If data is sent from http form (from the user frontend),
        save data from form into a new dict to make it mutable.
        Exclude empty values in the process.
        '''
        data = {}
        if request.form:
            for key in request.form:
                if request.form[key] != '':
                    data[key] = request.form[key]
                else:
                    data[key] = None
            result, status_code = post_task(data)
            if status_code == 400:
                flash(result)
            # redirect to the page the form is submitted.
            return redirect(request.environ.get('HTTP_REFERER', '/'))
        # if data from request json, direct load it in.
        elif request.json:
            data = request.json
        else:
            build_response({'error': 'Bad data for post request.'}, 400)
        result, status_code = post_task(data)
        return build_response(result, status_code)

    return build_response({}, 400)


def get_task(id: int, mode: Literal['tree', 'single', 'all'] = 'tree'
             ) -> tuple[dict, int]:
    '''
    Description
    -----------
    tree: recursively return all the subtasks that belong to the main id.

    single: return only the information of that task id.

    all: recursively return all task labeled with task levels

    Parameters
    ---------
    id: int
    Id of the main task to query

    mode: ['tree', 'single', 'all']
    Default to tree mode.

    Returns
    --------
    result: dict
    status_code" int
    Return the queried task in a dictionary with key tasks.
    If a bad mode is provided, return status code 400.
    '''
    db = get_db()
    if mode == 'tree':
        data = db.execute(
            '''
            WITH RECURSIVE TaskTree AS (
            SELECT id, title, parent_id, status, 1 AS Level
            FROM task
            WHERE id = ?
            UNION ALL
            SELECT t.id, t.title, t.parent_id, t.status, tt.Level + 1
            FROM task t
            INNER JOIN TaskTree tt ON t.parent_id = tt.id
            )
            SELECT * FROM TaskTree;
            ''', (id,)).fetchall()
        return {'tasks': RowsToList(data)}, 200

    elif mode == 'single':
        data = db.execute(
            '''
            SELECT id, title, parent_id, status
            FROM task
            WHERE id = ?
            ''', (id,)).fetchall()
        return {'tasks': RowsToList(data)}, 200

    elif mode == 'all':
        data = db.execute(
            '''
            WITH RECURSIVE TaskTree AS (
            SELECT id, title, parent_id, status, 1 AS Level
            FROM task
            where parent_id is null
            UNION ALL
            SELECT t.id, t.title, t.parent_id, t.status, tt.Level + 1
            FROM task t
            INNER JOIN TaskTree tt ON t.parent_id = tt.id
            )
            SELECT * FROM TaskTree
            ORDER BY id;
            ''').fetchall()
        return {'tasks': RowsToList(data)}, 200
    return {'error': 'Bad mode.'}, 400


def filter_task(filter: Literal['EMPTY', 'HALF', 'FULL']
                ) -> tuple[dict, int]:
    '''
    Description
    -----------
    Query tasks base on task status

    Parameters
    ---------
    filter: str

    ['EMPTY','HALF','FULL']

    Returns
    --------
    result: dict
    status_code: int
    Return the queried tasks in a dictionary with key tasks.
    '''
    db = get_db()
    data = db.execute(
        '''
    SELECT id, title, parent_id, status
    FROM task
    WHERE status = ?
    ''', (filter,)).fetchall()
    return {'tasks': RowsToList(data)}, 200


def post_task(data: dict[str, str | int]) -> tuple[dict, int]:
    '''
    Description
    -----------
    Insert a new task into db.
    Include title required check and parent id validation.

    Parameters
    ---------
    data: dict
    Includes title (required) and parent_id (optional)

    Returns
    --------
    result: dict
    status_code: int
    Return the queried tasks in a dictionary with key tasks.
    '''
    db = get_db()

    error = None
    if 'title' not in data:
        error = 'Missing title.'
    if 'parent_id' not in data:
        data['parent_id'] = None
    elif data['parent_id'] is None:
        pass
    elif not isinstance(data['parent_id'], int):
        try:
            data['parent_id'] = int(data['parent_id'])
        except ValueError:
            error = 'Parent_id has to be an integer.'

    if not error:
        try:
            resp = db.execute('''INSERT INTO task (title,parent_id)
                        VALUES (?,?)''',
                              (data['title'], data['parent_id']))
            id = resp.lastrowid
            db.commit()
        except db.IntegrityError:
            return {'error': 'Bad parent id.'}, 400
        data = db.execute(
            'SELECT id, title, parent_id, status FROM task where id=(?)',
            (id,)).fetchall()
        return {'tasks': RowsToList(data)}, 200

    return {'error': error}, 400


def patch_task(id: int, data: dict[str, str | int]) -> tuple[dict, int]:
    '''
    Description
    -----------
    Update task information in the database.
    Only changes on ['parent_id', 'status', 'title'] are allowed.


    Parameters
    ---------
    id: int
    id for the target task.

    data: dict
    available options are 'parent_id', 'status', 'title'

    Returns
    --------
    result: dict
    status_code: int
    Return task information after changes are made.
    '''
    db = get_db()
    allowed_columns = ['parent_id', 'status', 'title']
    safe_updates = {k: v for k, v in data.items() if k in allowed_columns}
    if not safe_updates:
        return {'error': 'All bad fields.'}, 400
    sql_set_parts = [f"{k} = ?" for k in safe_updates]
    sql_set_clause = ", ".join(sql_set_parts)
    params = tuple(safe_updates.values()) + (id,)
    try:
        cur = db.execute(
            f"UPDATE task SET {sql_set_clause} WHERE id = ?",
            params)
        if cur.rowcount == 0:
            return {'error': 'Id does not exist.'}, 400
        db.commit()
    except db.IntegrityError:
        return {'error': 'Bad data.'}, 400

    updated = db.execute(
        'SELECT id, title, parent_id, status FROM task where id=(?)',
        (id,)).fetchall()
    return {'tasks': RowsToList(updated)}, 200


def delete_task(id: int) -> tuple[dict, int]:
    '''
    Description
    -----------
    Delete a specific task.
    Deletion will failed if child tasks exist (IntegrationError)

    Parameters
    ---------
    id: int
    id for the target task.

    Returns
    --------
    result: dict
    status_code: int
    If successful, return a dictionary with
    tasks as key and empty string as value. Along with status code 204.
    Error information and 400 is returned if deletion failed.
    '''
    db = get_db()
    try:
        db.execute("DELETE FROM task where id=(?)",
                   (id,))
        db.commit()
        return {'tasks': ''}, 204
    except db.IntegrityError:
        return {'error':
                'Deletion unsucessful. Please delete all child tasks before deletion.'  # noqa
                }, 400


def show_lineage(id: int) -> tuple[dict, int]:
    '''
    Description
    -----------
    Show the lineage of the parent tasks all the way
    up to the root task. (a task with no parent id)

    The parent tasks are concat into a string with >> in between.

    Parameters
    ---------
    id:
    Target task id (the lowest level to query.)

    Returns
    --------
    result: dict
    status_code: int
    Dictionary with key lineage and value being the concatenated string
    '''
    db = get_db()
    data = db.execute(
        '''
        WITH RECURSIVE Lineage AS (
        SELECT id, title, parent_id, 1 AS Level
        FROM task
        WHERE id = ?
        UNION ALL
        SELECT t.id, t.title, t.parent_id, l.Level + 1
        FROM task t
        INNER JOIN Lineage l ON t.id = l.parent_id
        )
        SELECT title FROM Lineage
        ORDER BY Level;
        ''', (id,)).fetchall()
    result = ' >> '.join([task['title'] for task in data[1:]])
    return {'lineage': result}, 200


def get_available_parent(id: int) -> tuple[dict, int]:
    '''
    Description
    -----------
    Return the list of taks that can be assigned as the parent task
    for the current task.

    This is achieved by excluding
    all the child tasks under to the current task.

    Parameters
    ---------
    id:
    Target task id.

    Returns
    --------
    result: dict
    status_code: int
    Dictionary with key options and value being a list of avaliable tasks.
    '''
    db = get_db()
    data = db.execute(
        '''
            WITH RECURSIVE TaskTree AS (
            SELECT id, title, parent_id, status, 1 AS Level
            FROM task
            WHERE id = ?
            UNION ALL
            SELECT t.id, t.title, t.parent_id, t.status, tt.Level + 1
            FROM task t
            INNER JOIN TaskTree tt ON t.parent_id = tt.id
            )
            SELECT id,title FROM task
            where id not in (SELECT id FROM TaskTree)
        ''', (id,)).fetchall()
    return {'options': RowsToList(data)}, 200


def RowsToList(data: Row) -> list[dict | None]:
    '''
    Description
    -----------
    Convert Rows objects to simple dictionaries
    and store then in a list.

    Parameters
    ---------
    data: sqlite3.Row
    the data queried from db.execute.

    Returns
    --------
    result: list
    A empty list is returned if nothing is queried from the database.
    '''
    if not data:
        return []
    result = [dict(zip(item.keys(), item)) for item in data]
    return result
