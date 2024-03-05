from flask import (
    Blueprint)

bp = Blueprint('todo', __name__)


@bp.route('/')
def hello():
    return 'hellodsdddssdd'
