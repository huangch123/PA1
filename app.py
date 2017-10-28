######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Mona Jalal (jalal@bu.edu), Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'even more secret super secret string'  # Change this!

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
cursor.execute("SELECT email FROM User")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()

    query = "SELECT password FROM User WHERE email = %s"
    cursor.execute(query, (email,))

    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')
        # return '''
			#    <form action='login' method='POST'>
			# 	<input type='text' name='email' id='email' placeholder='email'></input>
			# 	<input type='password' name='password' id='password' placeholder='password'></input>
			# 	<input type='submit' name='submit'></input>
			#    </form></br>
		 #   <a href='/'>Home</a>
			#    '''

    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    query = "SELECT password FROM User WHERE email = %s"
    if cursor.execute(query, (email,)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email

            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('homepage.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', suppress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))

    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        query = "INSERT INTO USER (EMAIL, PASSWORD, FNAME, LNAME, DOB) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (email, password, fname, lname, dob))
        if gender:
            query = "UPDATE USER SET GENDER = %s WHERE EMAIL = %s"
            cursor.execute(query, (gender, email))
        if hometown:
            query = "UPDATE USER SET HOMETOWN = %s WHERE EMAIL = %s"
            cursor.execute(query, (hometown, email))
        conn.commit()
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('homepage.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))


def getUsersPhotos(uid):
    cursor = conn.cursor()

    query = "SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = %s"
    cursor.execute(query, (uid,))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()

    query = "SELECT user_id FROM User WHERE email = %s"
    cursor.execute(query, (email,))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()

    query = "SELECT email FROM User WHERE email = %s"
    if cursor.execute(query, (email,)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    query = "SELECT fname, lname FROM User WHERE email = %s"
    cursor.execute(query, (flask_login.current_user.id))
    nameData = cursor.fetchall()
    fname = str(nameData[0][0])
    lname = str(nameData[0][1])
    userName = fname + " " + lname

    return render_template('homepage.html', name= userName, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        #cursor.execute(
        #    "INSERT INTO Pictures (imgdata, user_id, caption) VALUES ('photo_data', 'uid', 'caption')")
        cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s)",
                       (photo_data, uid, caption))
        #cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption) VALUES (?, ?, ?)", (photo_data, uid, caption))
        conn.commit()
        return render_template('homepage.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')


# end photo uploading code


# default homepage
@app.route('/', methods=['GET'])
def homepage():
    return render_template("homepage.html")

# shows specific photo
@app.route('/photo', methods=['Get'])
def photo():
    return render_template("photo.html")

@app.route('/search_friends', methods=['GET', 'POST'])
def search_friends():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')

    users = []
    if fname or lname or email:
        query = "SELECT EMAIL, FNAME, LNAME FROM USER"
        tuple = ()
        query += " WHERE 1 = 1"
        if fname:
            query += " AND FNAME = %s"
            tuple += (fname,)
        if lname:
            query += " AND LNAME = %s"
            tuple += (lname,)
        if email:
            query += " AND EMAIL = %s"
            tuple += (email,)
        cursor = conn.cursor()
        cursor.execute(query, tuple)
        data = cursor.fetchall()

        for i in range(len(data)):
            user = []
            user.append(str(data[i][0]))
            user.append(str(data[i][1]))
            user.append(str(data[i][2]))
            users.append(user)
        print(users)

    return render_template('search_friends.html', users=users)

@app.route('/my_friends', methods=['GET'])
def my_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    query = "SELECT U.FNAME, U.LNAME FROM FRIENDSHIP F, USER U WHERE F.UID1 = %s AND F.UID2 = U.UID"
    cursor.execute(query, uid)
    data = cursor.fetchall()
    friends = []
    for i in range(len(data)):
        friend = []
        friend.append(str(data[i][0]))
        friend.append(str(data[i][1]))
        friends.append(friend)
    print(friends)
    return render_template('my_friends.html', friends=friends)

@app.route('/search')
def search():
    return render_template('search.html')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
