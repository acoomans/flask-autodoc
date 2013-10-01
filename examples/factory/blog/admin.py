from flask import current_app, Blueprint, render_template
from flask.ext.autodoc import Autodoc

admin = Blueprint('admin', __name__, url_prefix='/admin')
from doc import auto

@admin.route('/')
@auto.doc(groups=['private'])
def index():
    """Admin interface."""
    return "Admin interface"
