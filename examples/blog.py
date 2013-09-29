from flask import Flask, redirect
from json import dumps, JSONEncoder
from flask.ext.autodoc import Autodoc

app = Flask(__name__)
app.debug = True
auto = Autodoc(app)

users = []
posts = []

class User(object):
    def __init__(self, username):
        self.username = username
        users.append(self)
        self.id = users.index(self)

class Post(object):
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        posts.append(self)
        self.id = posts.index(self)

u = User("acoomans")
Post("First post", "This is the first awesome post", u)
Post("Second post", "This is another even more awesome post", u)

@app.route("/")
@app.route("/posts")
@auto.doc(groups=["posts", 'public', "private"])
def get_posts():
    """Returns all posts."""
    return dumps(posts)

@app.route('/post/<int:id>')
@auto.doc(groups=["posts", 'public', "private"])
def get_post(id):
    """This returns a post with an id."""
    return dumps(posts[id])

@app.route('/users')
@auto.doc(groups=["users", 'public', "private"])
def get_users():
    """This returns all users."""
    return dumps(users)

@app.route('/user/<int:id>')
@auto.doc(groups=["users", 'public', "private"])
def get_user(id):
    """This returns a user with a given id."""
    return dumps(users[id])


@app.route('/users', methods=["POST"])
@auto.doc(groups=["users", 'private'])
def post_user(id):
    """This creates a new user."""
    User("frank")
    redirect("/users")

@app.route('/admin', methods=["GET"])
@auto.doc(groups=['private'])
def admin(id):
    """Admin interface."""
    return "Admin interface"

@app.route('/doc')
@app.route('/doc/public')
def public_doc():
    return auto.html(groups=["public"], title="Blog Documentation")

@app.route('/doc/private')
def private_doc():
    return auto.html(groups=["private"], title="Private Documentation")

if __name__ == "__main__":
    app.run()