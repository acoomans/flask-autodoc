from flask import Flask
from flask.ext.autodoc import Autodoc
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
auto = Autodoc(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
manager = APIManager(app, flask_sqlalchemy_db=db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=True)
    content = db.Column(db.String(300))

# Create API endpoints for SQLAlchemy models:
manager.create_api(User)
manager.create_api(Post, methods=['GET', 'POST', 'DELETE'])

# Decorate all endpoints with Autodoc.doc():
for endpoint, function in app.view_functions.iteritems():
    app.view_functions[endpoint] = auto.doc()(function)

if __name__ == '__main__':
    app.run()
