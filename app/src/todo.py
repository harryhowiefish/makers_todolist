from flask import (
    Blueprint, request, session, current_app,
    render_template, redirect, url_for)
from app.src import api, db
import uuid
import os

bp = Blueprint('todo', __name__)


@bp.route('/')
def show_all():
    if 'uid' not in session:
        session['uid'] = uuid.uuid4()
        db_filename = os.path.join(
            current_app.config['DATABASE_DIR'],
            f"session_{session['uid']}.sqlite")
        db.init_db(db_filename)
        session['DATABASE'] = db_filename

    data, _ = api.get_task(id=None, mode='all')
    trees = tasks_to_trees(data['tasks'])
    # this option is for setting the parent task for a new added task.
    parent_options = list_parent_options(data['tasks'])
    return render_template('index.html', tasks=trees,
                           parents=parent_options)


@bp.route('/<id>')
def show_task(id):
    data, _ = api.get_task(id, mode='tree')
    trees = tasks_to_trees(data['tasks'])
    if trees:
        tree = trees[0]
    else:
        return '', 204
    # this option is for changing the parent task for the current task.
    edit_task_options, _ = api.get_available_parent(id)
    # this option is for setting the parent task for a new added task.
    add_task_options = list_parent_options(data['tasks'])
    return render_template('single_task.html', main_task=tree,
                           tasks=tree.get('sub_tasks', []),
                           edit_parents=edit_task_options['options'],
                           new_parents=add_task_options
                           )


@bp.route('/filter')
def filter():
    mode = request.args.get('mode', '', str).lower()
    if mode == 'ongoing':
        data, _ = api.filter_task(filter='HALF')
    elif mode == 'pending':
        data, _ = api.filter_task(filter='EMPTY')
    elif mode == 'completed':
        data, _ = api.filter_task(filter='FULL')
    else:
        # if mode is a weird value, then query all tasks
        data, _ = api.get_task(id=None, mode='all')

    # add lineage information to tasks
    for task in data['tasks']:
        lineage, _ = api.show_lineage(task['id'])
        task.update(lineage)

    return render_template('filter.html', tasks=data['tasks'])


@bp.route('/submit', methods=['POST'])
def handle_submit():
    '''
    this is added as a router for PATCH and DELETE requests as
    they are not supported in HTTP Form.
    '''
    process = request.args.get('process', None, type=str)
    data = request.form.to_dict()
    # set empty string from form to None type
    for key, value in data.items():
        if value == '':
            data[key] = None

    if process == 'delete':
        api.delete_task(data['id'])
        return redirect(request.environ.get('HTTP_REFERER', '/'))
    elif process == 'edit':
        api.patch_task(id=data['id'], data=data)
        print(data)
        if data['parent_id'] is None:
            return redirect(url_for('todo.show_all'))
        return redirect(url_for('todo.show_task', id=data['parent_id']))
    return 'Process not known', 404


def tasks_to_trees(tasks: list[dict]) -> list[dict]:
    '''
    Description
    -----------
    Reformat the queried data into a tree format.
    Task are linked based on parent_id and organized under
    the sub_task key.

    Parameters
    ---------
    tasks: list[dict]
    The queried tasks from database.

    Returns
    --------
    trees: list[dict]
    Each tree starts with a root_task and sub_tasks located under it.
    i.e. {'id': 1, 'title': 'Main_task_1',
         'sub_tasks': [{'id': 3, 'title': 'Sub_task_1'}]
         }
    '''
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


def list_parent_options(tasks: list[dict]) -> list[dict]:
    '''
    Description
    -----------
    List all the title and id of the tasks that are in the current task list.
    This is used to show all the available parent tasks
    when creating a new task.

    Parameters
    ---------
    tasks: list[dict]
    The queried tasks from database.

    Returns
    --------
    options: list
    A list of dictionary containing title and id.
    '''
    options = []
    for task in tasks:
        filtered_dict = {k: v for k, v in task.items() if k in ['title', 'id']}
        options.append(filtered_dict)
    return options
