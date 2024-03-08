from flask import (
    Blueprint, request, jsonify, redirect, url_for)
from .db import get_db
from sqlite3 import Row

bp = Blueprint('api', __name__, url_prefix="/api/v1")


@bp.route('/tasks', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def task_by_id():
    id = request.args.get('id', default=None, type=int)
    mode = request.args.get('mode', default='', type=str).lower()
    filter = request.args.get('filter', default='', type=str).lower()

    if id is not None:
        if request.method == 'GET':
            if mode == '':
                mode = 'tree'
            result, status_code = get_task(id, mode)
            return jsonify(result), status_code

        if request.method == 'PATCH':
            data = request.json
            result, status_code = patch_task(id, data)
            return jsonify(result), status_code

        elif request.method == 'DELETE':
            result, status_code = delete_task(id)
            return jsonify(result), status_code

    if request.method == 'GET':
        result, status_code = filter_task(filter)
        return jsonify(result), status_code

    elif request.method == 'POST':
        data = {}
        if request.form:
            print('na?')
            for key in request.form:
                if request.form[key] != '':
                    data[key] = request.form[key]
                else:
                    data[key] = None
            post_task(data)
            return redirect(url_for('todo.show_all'))
        elif request.json:
            data = request.json
            print(data)
        result, status_code = post_task(data)
        return jsonify(result), status_code

    return '', 400


def get_task(id, mode):
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


def filter_task(filter):
    db = get_db()
    data = db.execute(
        '''
    SELECT id, title, parent_id, status
    FROM task
    WHERE status = ?
    ''', (filter,)).fetchall()
    return {'tasks': RowsToList(data)}, 200


def post_task(data):
    db = get_db()

    error = None
    if 'title' not in data:
        error = 'Missing title.'
    if 'parent_id' not in data:
        data['parent_id'] = None

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


def patch_task(id, data):
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


def delete_task(id):
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


def show_lineage(id):
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


def get_avaliable_parent(id):
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


def RowsToList(data: Row) -> list:
    if not data:
        return []
    result = [dict(zip(item.keys(), item)) for item in data]
    return result
