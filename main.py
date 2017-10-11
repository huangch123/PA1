import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


@app.route('/')
def homepage():
    return render_template("homepage.html")


''''@app.route('/')
def hello_world():
    return '<b>Hello World!</b>'

@app.route('/')
def homepage():
    return "Method used: %s" % request.method
    '''

'''@app.route('/profile/<username>')
def profile(username):
    return "<h1> hello %s </h1>" % username'''


@app.route('/profile/<name>')
def profile(name):
    return render_template("profile.html", name=name)


@app.route('/posts/<int:post_id>')
def posts(post_id):
    return "<h2> post id is %s </h2>" % post_id


@app.route("/salmon", methods=['GET', 'POST'])
def salmon():
    if request.method == 'POST':
        return "<h3> You are using POST </h3>"
    else:
        return "<h3> You are using GET </h3>"


@app.route('/bacon', methods=['GET', 'POST'])
def bacon():
    if request.method == 'POST':
        return "Method used: POST"
    else:
        return '<form action="/bacon" method="POST">' \
               '<input type="submit" value="submit"/></form>'


@app.route('/post/<int:post_id>')
def posts(post_id):
    return render_template("post.html", post_id=post_id)


@app.route('/')
@app.route('/<user>')
def index(user=None):
    return render_template("user.html", user=user)


@app.route('/shopping')
def shopping():
    food = ['salmon', 'chicken', 'beef']
    return render_template("shopping.html", food=food)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


if __name__ == '__main__':
    app.run(debug=True)
