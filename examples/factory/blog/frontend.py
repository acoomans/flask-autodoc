from flask import current_app, Blueprint, render_template, redirect
from flask.ext.autodoc import Autodoc
from json import dumps

frontend = Blueprint('frontend', __name__, url_prefix='/blog')
from doc import auto

users = []
posts = []

class User(object):
    def __init__(self, username):
        self.username = username
        users.append(self)
        self.id = users.index(self)
    def __repr__(self):
        return dumps(self.__dict__)

class Post(object):
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        posts.append(self)
        self.id = posts.index(self)
    def __repr__(self):
        return dumps(self.__dict__)

u = User("acoomans")
Post("First post", "This is the first awesome post", u)
Post("Second post", "This is another even more awesome post", u)

@frontend.route("/")
@frontend.route("/posts")
@auto.doc(groups=["posts", 'public', "private"])
def get_posts():
    """Returns all posts."""
    return "%s" % posts

@frontend.route('/post/<int:id>')
@auto.doc(groups=["posts", 'public', "private"])
def get_post(id):
    """This returns a post with an id."""
    return "%s" % posts[id]

@frontend.route('/users')
@auto.doc(groups=["users", 'public', "private"])
def get_users():
    """This returns all users."""
    return "%s" % users

@frontend.route('/user/<int:id>')
@auto.doc(groups=["users", 'public', "private"])
def get_user(id):
    """This returns a user with a given id."""
    return "%s" %  users[id]


@frontend.route('/users', methods=["POST"])
@auto.doc(groups=["users", 'private'])
def post_user(id):
    """This creates a new user."""
    User("frank")
    redirect("/users")