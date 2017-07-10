from flask import Blueprint
from flask_autodoc import Autodoc


doc = Blueprint('doc', __name__, url_prefix='/doc')
auto = Autodoc()


@doc.route('/')
@doc.route('/public')
def public_doc():
    return auto.html(groups=['public'], title='Blog Documentation')


@doc.route('/private')
def private_doc():
    return auto.html(groups=['private'], title='Private Documentation')
