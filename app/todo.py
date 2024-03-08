from flask import (
    Blueprint, request, render_template, redirect, url_for)
from app import api
bp = Blueprint('todo', __name__)


@bp.route('/')
def show_all():
    data, _ = api.get_task(id=None, mode='all')
    trees = tasks_to_trees(data['tasks'])
    parent_options = list_parent_options(data['tasks'])
    return render_template('index.html', tasks=trees,
                           parents=parent_options)


@bp.route('/filter')
def filter():
    mode = request.args.get('mode', None, str)
    if mode == 'ongoing':
        data, _ = api.filter_task(filter='HALF')
    elif mode == 'pending':
        data, _ = api.filter_task(filter='EMPTY')
    elif mode == 'completed':
        data, _ = api.filter_task(filter='FULL')
    else:
        data, _ = api.get_task(id=None, mode='all')
    for task in data['tasks']:
        lineage, _ = api.show_lineage(task['id'])
        task.update(lineage)
    return render_template('filter.html', tasks=data['tasks'],
                           )


@bp.route('/<id>')
def show_task(id):
    data, _ = api.get_task(id, mode='tree')
    trees = tasks_to_trees(data['tasks'])
    parent_options, _ = api.get_avaliable_parent(id)
    return render_template('single_task.html',
                           tasks=trees, parents=parent_options['options'])


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
        api.patch_task(id=data['id'], data=data)
        return redirect(url_for('todo.show_all'))
    return 'Process not known', 404


def tasks_to_trees(tasks):
    task_dict = {task['id']: task for task in tasks}
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
