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
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
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


@app.route('/profile/<name>')
def profile(name):
    return render_template("profile.html", name=name)


@app.route('/')
@app.route('/<user>')
def index(user=None):
    return render_template("user.html", user=user)

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/photo')
def photo():
    return render_template("photo.html")

@app.route('/unauthorized')
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


if __name__ == '__main__':
    app.run(debug=True)
