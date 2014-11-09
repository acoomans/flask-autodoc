from flask import Blueprint

from .doc import auto


admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@auto.doc(groups=['private'])
def index():
    """Admin interface."""
    return 'Admin interface'
