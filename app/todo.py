from flask import (
    Blueprint, request, render_template, redirect, url_for)
from app import api
import json
bp = Blueprint('todo', __name__)


@bp.route('/')
def show_all():
    response = api.get_task(id=None, mode='all')
    data = json.loads(response.data)
    trees = tasks_to_trees(data['data'])
    parent_options = list_parent_options(data['data'])
    return render_template('index.html', tasks=trees,
                           parents=parent_options)


@bp.route('/filter')
def filter():
    mode = request.args.get('mode', None, str)
    if mode == 'ongoing':
        response = api.filter_task(filter='HALF')
    elif mode == 'pending':
        response = api.filter_task(filter='EMPTY')
    elif mode == 'completed':
        response = api.filter_task(filter='FULL')
    else:
        response = api.get_task(id=None, mode='all')
    data = json.loads(response.data)
    for task in data['data']:
        lineage_resp = api.show_lineage(task['id'])
        task.update(json.loads(lineage_resp.data))
    return render_template('filter.html', tasks=data['data'],
                           )


@bp.route('/<id>')
def show_task(id):
    response = api.get_task(id, mode='tree')
    data = json.loads(response.data)
    trees = tasks_to_trees(data['data'])
    response = api.get_avaliable_parent(id)
    parent_options = json.loads(response.data)['data']
    print(parent_options)
    return render_template('single_task.html',
                           tasks=trees, parents=parent_options)


@bp.route('/submit', methods=['POST'])
def handle_submit():
    process = request.args.get('process', None, type=str)
    data = request.form.to_dict()
    for key, value in data.items():
        if value == '':
            data[key] = None
    if process == 'delete':
        api.delete_task(data['id'])
        return redirect(url_for('todo.show_all'))
    elif process == 'edit':
        print(data)
        api.patch_task(id=data['id'], data=data)
        return redirect(url_for('todo.show_all'))
    return 'Process not known', 404


def cleanup_task(task: dict):
    return {k: v for k, v in task.items() if k not in ['Level']}


def tasks_to_trees(tasks):
    task_dict = {task['id']: cleanup_task(task) for task in tasks}
    root_tasks = []

    for task in tasks:
        if task['Level'] != 1:
            parent = task_dict.get(task['parent_id'])
            if parent is not None:
                if 'sub_tasks' not in parent:
                    parent['sub_tasks'] = []
                parent['sub_tasks'].append(task_dict[task['id']])
        else:
            root_tasks.append(task_dict[task['id']])

    return root_tasks


def list_parent_options(tasks):
    options = []
    for task in tasks:
        filtered_dict = {k: v for k, v in task.items() if k in ['title', 'id']}
        options.append(filtered_dict)
    return options
