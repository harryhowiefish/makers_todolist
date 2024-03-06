from flask import (
    Blueprint, request, jsonify)
from .db import get_db
from sqlite3 import Row

bp = Blueprint('api', __name__, url_prefix="/api/v1")


@bp.route('/tasks', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def task_by_id():
    id = request.args.get('id', default=None, type=int)

    if id is not None:
        if request.method == 'GET':
            mode = request.args.get('mode', default='tree', type=str).lower()
            return get_task(id, mode)

        elif request.method == 'PATCH':
            data = request.json
            return patch_task(id, data)

        elif request.method == 'DELETE':
            return delete_task(id)

    if request.method == 'POST':
        data = request.json
        return post_task(data)

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
        return jsonify(RowsToDict(data))
    elif mode == 'single':
        data = db.execute(
            '''
            SELECT id, title, parent_id, status
            FROM task
            WHERE id = ?
            ''', (id,)).fetchall()
        return jsonify(RowsToDict(data))
    return jsonify({'error': 'Bad mode.'}), 400


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
            return jsonify({'error': 'Bad parent id.'}), 400
        data = db.execute(
            'SELECT id, title, parent_id, status FROM task where id=(?)',
            (id,)).fetchall()
        return jsonify(RowsToDict(data))

    return jsonify({'error': error}), 400


def patch_task(id, data):
    db = get_db()
    allowed_columns = ['parent_id', 'status', 'title']
    safe_updates = {k: v for k, v in data.items() if k in allowed_columns}
    if not safe_updates:
        return jsonify({'error':
                        'All bad fields.'
                        }), 400
    sql_set_parts = [f"{k} = ?" for k in safe_updates]
    sql_set_clause = ", ".join(sql_set_parts)
    params = tuple(safe_updates.values()) + (id,)
    try:
        cur = db.execute(
            f"UPDATE task SET {sql_set_clause} WHERE id = ?",
            params)
        if cur.rowcount == 0:
            return jsonify({'error':
                            'Id does not exist.'
                            }), 400
        db.commit()
    except db.IntegrityError:
        return jsonify({'error':
                        'Bad data.'
                        }), 400

    updated = db.execute(
        'SELECT id, title, parent_id, status FROM task where id=(?)',
        (id,)).fetchall()
    return jsonify(RowsToDict(updated))


def delete_task(id):
    db = get_db()
    try:
        db.execute("DELETE FROM task where id=(?)",
                   (id,))
        db.commit()
        return '', 204
    except db.IntegrityError:
        return jsonify({'error':
                        'Deletion unsucessful. Please delete all child tasks before deletion.'  # noqa
                        }), 400


def RowsToDict(data: Row, key_name: str = 'data') -> list:
    if not data:
        return {}
    result = [dict(zip(item.keys(), item)) for item in data]
    return {key_name: result}
