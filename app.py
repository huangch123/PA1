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
from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory
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

def get_info(email):
    query = "SELECT fname, lname, dob, hometown, gender FROM User WHERE email = %s"
    if cursor.execute(query, (email,)):
        nameData = cursor.fetchall()
        fname = str(nameData[0][0])
        lname = str(nameData[0][1])
        username = fname + " " + lname
        dob = str(nameData[0][2])
        hometown = str(nameData[0][3])
        gender = str(nameData[0][4])
        info = (username, dob, hometown, gender)
        return info
    else:
        return

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    user.name = get_info(email)[0]
    user.dob = get_info(email)[1]
    user.hometown = get_info(email)[2]
    user.gender = get_info(email)[3]
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
    # user.is_authenticated = request.form['password'] == pwd
    if request.form['password'] == pwd:
        return user
    else:
        return None


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
    return render_template('login.html', message='Incorrect email or password')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    # return render_template('homepage.html', message='Logged out')
    return flask.redirect(flask.url_for('homepage'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return render_template('register.html', suppress='True')
    else:
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            gender = request.form.get('gender')
            dob = request.form.get('dob')
            hometown = request.form.get('hometown')
        except:
            print("couldn't find all tokens(1)")  # this prints to shell, end users will not see this (all print statements go to shell)
            # return flask.redirect(flask.url_for('register', suppress='False'))
            return render_template('register.html')

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
            # return render_template('homepage.html', name=email, message='Account Created!')
            return flask.redirect(flask.url_for('protected'))
        else:
            print("couldn't find all tokens(2)")
            # return flask.redirect(flask.url_for('register', suppress='False'))
            return render_template('register.html')


def getUsersPhotos(uid):
    cursor = conn.cursor()

    query = "SELECT P.PID, P.CAPTION, P.DATA FROM PHOTO P, ALBUM A WHERE P.AID = A.AID AND A.UID = %s"
    cursor.execute(query, uid)
    return cursor.fetchall()  # NOTE list of tuples, [(pid, caption, data), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()

    query = "SELECT UID FROM User WHERE email = %s"
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

def checkFriendship(email1, email2):
    cursor = conn.cursor()
    query = "SELECT * FROM USER U1 , USER U2, FRIENDSHIP F WHERE F.UID1 = U1.UID AND F.UID2 = U2.UID AND U1.EMAIL = %s AND U2.EMAIL = %s"
    return cursor.execute(query, (email1, email2)) == 1

# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('profile.html', message="Here's your profile")


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
        album_id = request.form.get('album')
        tags = request.form.get('tag')
        caption = request.form.get('caption')
        ext = '.' + str(imgfile.filename).rsplit('.', 1)[1]

        tags = str(tags).split(' ')
        for tag in tags:
            cursor.execute("SELECT HASHTAG FROM TAG WHERE HASHTAG = %s", tag)
            if not cursor.fetchall():
                cursor.execute("INSERT INTO TAG VALUES (%s)", tag)
                conn.commit()
        cursor.execute("SELECT MAX(PID) FROM PHOTO")
        data = cursor.fetchone()
        if data[0]:
            file_name = str(int(data[0]) + 1) + ext
        else:
            file_name = '1' + ext
        if imgfile and imgfile.filename != '':
            imgfile.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        cursor.execute("INSERT INTO PHOTO (CAPTION, DATA, AID) VALUES (%s, %s, %s)", (caption, file_name, album_id))
        for tag in tags:
            cursor.execute("INSERT INTO ASSOCIATE VALUES ( ( SELECT MAX(PID) FROM PHOTO ), %s)", tag)
        conn.commit()
        return render_template('homepage.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid))
    # method is GET so we return a  HTML form to upload the a photo
    else:
        query = "SELECT AID, NAME FROM ALBUM WHERE UID = %s"
        cursor.execute(query, getUserIdFromEmail(flask_login.current_user.id))
        albums = cursor.fetchall()

        query = "SELECT HASHTAG FROM TAG"
        cursor.execute(query)
        tags = cursor.fetchall()
        return render_template('upload.html', albums=albums, tags=tags)

# end photo uploading code


# default homepage
@app.route('/', methods=['GET'])
def homepage():
    query = "SELECT U.FNAME, U.LNAME, TMP1.photoCnt + TMP2.commentCnt AS TOTAL FROM USER U, ( SELECT A.UID , COUNT(*) AS photoCnt FROM PHOTO P, ALBUM A WHERE P.AID = A.AID GROUP BY A.UID ) AS TMP1, ( SELECT C.UID, COUNT(*) AS commentCnt FROM COMMENT C GROUP BY C.UID ) AS TMP2 WHERE U.UID = TMP1.UID AND TMP1.UID = TMP2.UID GROUP BY U.UID ORDER BY TOTAL DESC LIMIT 10"
    cursor.execute(query)
    data = cursor.fetchall()
    top_users = []
    for i in range(len(data)):
        info = [str(data[i][0]), str(data[i][1]), str(data[i][2])]
        top_users.append(info)
    print(top_users)

    query = "SELECT HASHTAG, COUNT(PID) FROM ASSOCIATE GROUP BY HASHTAG ORDER BY COUNT(PID) DESC LIMIT 10"
    cursor.execute(query)
    data = cursor.fetchall()
    top_tags = []
    for i in range(len(data)):
        top_tags.append(str(data[i][0]))
    print(top_tags)

    query = "SELECT P.PID, P.DATA FROM PHOTO P, FAVORITE F WHERE P.PID = F.PID GROUP BY P.PID ORDER BY COUNT(F.UID) DESC LIMIT 20"
    cursor.execute(query)
    data = cursor.fetchall()
    top_photos = []
    for i in range(len(data)):
        top_photos.append([str(data[i][0]), str(data[i][1])])
    print(top_photos)

    return render_template('homepage.html', top_users=top_users, top_tags=top_tags, top_photos=top_photos)

@app.route('/albums', methods=['Get', 'POST'])
def albums():
    if request.method == 'GET':
        query = "SELECT AID, NAME FROM ALBUM WHERE UID = %s"
        cursor.execute(query, getUserIdFromEmail(flask_login.current_user.id))
        albums = cursor.fetchall()
        return render_template("albums.html", albums=albums)
    else:
        album_id = request.form.get('album_id')
        if album_id:
            query = "SELECT PID, DATA FROM PHOTO WHERE AID = %s"
            cursor.execute(query, album_id)
            photos = cursor.fetchall()
            return render_template("album.html", photos=photos)
        else:
            new_album = request.form.get('albumName')
            cursor.execute("INSERT INTO ALBUM (NAME, UID) VALUES (%s, %s)", (new_album, getUserIdFromEmail(flask_login.current_user.id)))
            conn.commit()
            query = "SELECT AID, NAME FROM ALBUM WHERE UID = %s"
            cursor.execute(query, getUserIdFromEmail(flask_login.current_user.id))
            albums = cursor.fetchall()
            return render_template("albums.html", albums=albums)

@app.route('/album/<int:album_id>', methods=['Get'])
def album(album_id):
    if request.method == 'GET':
        query = "SELECT PID, DATA FROM PHOTO WHERE AID = %s"
        cursor.execute(query, album_id)
        photos = cursor.fetchall()
        return render_template("album.html", photos=photos)
    else:
        photo_id = request.form.get('photo_id')
        query = "SELECT CAPTION, DATA FROM PHOTO WHERE PID = %s"
        cursor.execute(query, photo_id)
        photo = cursor.fetchone()

        return render_template("photo.html", photo=photo)

@app.route('/upload/<path:filename>')
def get_photo(filename):
    return send_from_directory("upload/", filename, as_attachment=True)

def get_photo_info(photo_id):
    uid = getUserIdFromEmail(flask_login.current_user.id)

    query = "SELECT PID, CAPTION, DATA FROM PHOTO WHERE PID = %s"
    cursor.execute(query, photo_id)
    photo = cursor.fetchone()

    query = "SELECT HASHTAG FROM ASSOCIATE WHERE PID = %s"
    cursor.execute(query, photo_id)
    tags = cursor.fetchall()

    query = "SELECT C.CONTENT, C.DOC, U.FNAME, U.LNAME FROM COMMENT C, USER U WHERE C.UID = U.UID AND C.PID = %s"
    cursor.execute(query, photo_id)
    comments = cursor.fetchall()

    query = "SELECT U.FNAME, U.LNAME FROM FAVORITE F, USER U WHERE F.UID = U.UID AND PID = %s"
    cursor.execute(query, photo_id)
    likes = cursor.fetchall()

    query = "SELECT * FROM FAVORITE WHERE PID = %s AND UID = %s"
    cursor.execute(query, (photo_id, uid))
    if cursor.fetchone():
        liked = True
    else:
        liked = False

    print(photo, tags, comments, likes)
    return render_template('photo.html', photo=photo, tags=tags, comments=comments, likes=likes, liked=liked)

# show specific photo
@app.route('/photo/<int:photo_id>', methods=['Get', 'POST'])
def photo(photo_id):
    if request.method == 'GET':
        return get_photo_info(photo_id)
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        if request.form.get('photoBtn') == 'comment':
            text = request.form.get('commentText')
            query = "INSERT INTO COMMENT (CONTENT, DOC, UID, PID) VALUES (%s, CURRENT_TIMESTAMP, %s, %s)"
            cursor.execute(query, (text, uid, photo_id))
            conn.commit()

        if request.form.get('photoBtn') == 'like':
            query = "INSERT INTO FAVORITE (UID, PID, DOC) VALUES (%s, %s, CURRENT_TIMESTAMP)"
            cursor.execute(query, (uid, photo_id))
            conn.commit()

        if request.form.get('photoBtn') == 'unlike':
            query = "DELETE FROM FAVORITE WHERE UID = %s AND PID = %s"
            cursor.execute(query, (uid, photo_id))
            conn.commit()

        return get_photo_info(photo_id)

@app.route('/search_friends', methods=['GET', 'POST'])
def search_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    uid2 = request.form.get('addFriendBtn')
    if uid2:
        query = "INSERT INTO FRIENDSHIP VALUES (%s, %s)"
        cursor.execute(query, (uid, uid2))
        cursor.execute(query, (uid2, uid))
        conn.commit()

    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    inputs = [fname, lname, email]

    users = []
    if fname or lname or email:
        query = "SELECT UID, FNAME, LNAME FROM USER"
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
        cursor.execute(query, tuple)
        data = cursor.fetchall()

        for i in range(len(data)):
            user = []
            user.append(str(data[i][0]))
            user.append(str(data[i][1]) + ' ' + str(data[i][2]))
            if checkFriendship(flask_login.current_user.id, str(data[i][0])) or flask_login.current_user.id == str(data[i][0]):
                user.append('1')
            else:
                user.append('0')
            users.append(user)
        print(users)

    query = "SELECT DISTINCT U3.UID, U3.FNAME, U3.LNAME, COUNT(U3.UID) FROM USER U, FRIENDSHIP F, USER U2, FRIENDSHIP F2, USER U3 WHERE U.UID = F.UID1 AND F.UID2 = U2.UID AND U2.UID = F2.UID1 AND F2.UID2 = U3.UID AND U.UID <> U3.UID AND U.UID = %s GROUP BY U3.UID ORDER BY COUNT(U3.UID) DESC;"
    cursor.execute(query, uid)
    data = cursor.fetchall()
    rec = []
    for i in range(len(data)):
        rec.append([data[i][0], data[i][1] + ' ' + data[i][2], data[i][3]])

    return render_template('search_friends.html', users=users, search_info=inputs, rec=rec)

@app.route('/my_friends', methods=['GET'])
def my_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    query = "SELECT U.FNAME, U.LNAME FROM FRIENDSHIP F, USER U WHERE F.UID1 = %s AND F.UID2 = U.UID"
    cursor.execute(query, uid)
    data = cursor.fetchall()
    friends = []
    for i in range(len(data)):
        friend = []
        friend.append(str(data[i][0]))
        friend.append(str(data[i][1]))
        friends.append(friend)
    return render_template('my_friends.html', friends=friends)

@app.route('/search', methods=['GET', 'POST'])
def search():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'GET':
        query = "SELECT HASHTAG, COUNT(PID) FROM ASSOCIATE GROUP BY HASHTAG ORDER BY COUNT(PID) DESC LIMIT 10"
        cursor.execute(query)
        data = cursor.fetchall()
        top_tags = []
        for i in range(len(data)):
            top_tags.append(str(data[i][0]))
        print(top_tags)
        return render_template('search.html', top_tags=top_tags)

    else:
        radio = request.form.get('radioAll')
        tags = str(request.form.get('searchTags')).split(' ')
        if len(tags) == 1:
            tag = tags[0]
            if radio == 'on':
                query = "SELECT P.PID, P.DATA FROM PHOTO P, ASSOCIATE A WHERE P.PID = A.PID AND A. HASHTAG = %s"
                cursor.execute(query, tag)
            else:
                query = "SELECT P.PID, P.DATA, Al.UID FROM PHOTO P, ASSOCIATE A, ALBUM AL WHERE AL.AID = P.AID AND P.PID = A.PID AND A. HASHTAG = %s AND AL.UID = %s"
                cursor.execute(query, (tag, uid))
            data = cursor.fetchall()
            tag_photos = []
            for i in range(len(data)):
                tag_photos.append([str(data[i][0]), str(data[i][1])])
            print(tag_photos)
        else:
            all_photos = set()
            query = "SELECT PID FROM PHOTO"
            cursor.execute(query)
            data = cursor.fetchall()
            for i in range(len(data)):
                all_photos.add(str(data[i][0]))

            for tag in tags:
                tag_photos = set()
                if radio == 'on':
                    query = "SELECT PID FROM ASSOCIATE A WHERE HASHTAG = %s"
                    cursor.execute(query, tag)
                else:
                    query = "SELECT P.PID FROM PHOTO P, ASSOCIATE A, ALBUM AL WHERE AL.AID = P.AID AND P.PID = A.PID AND A. HASHTAG = %s AND AL.UID = %s"
                    cursor.execute(query, (tag, uid))
                data = cursor.fetchall()
                for i in range(len(data)):
                    tag_photos.add(str(data[i][0]))
                all_photos = all_photos.intersection(tag_photos)

            tag_photos = []
            for tag_photo in all_photos:
                query = "SELECT PID, DATA FROM PHOTO WHERE PID = %s"
                cursor.execute(query, tag_photo)
                data = cursor.fetchall()
                tag_photos.append([data[0][0],data[0][1]])
            print(tag_photos)

        query = "SELECT HASHTAG, COUNT(PID) FROM ASSOCIATE GROUP BY HASHTAG ORDER BY COUNT(PID) DESC LIMIT 10"
        cursor.execute(query)
        data = cursor.fetchall()
        top_tags = []
        for i in range(len(data)):
            top_tags.append(str(data[i][0]))
        print(top_tags)
        return render_template('search.html', top_tags=top_tags, photos=tag_photos)

# @app.route('/album', methods=['GET'])
# def delete_photo(photo_id, album_id):
#     # delete photo from database
#     return render_template('album.html/album_id')

# @app.route('/albums', methods=['Get'])
# def delete_album(album_id):
#     # delete album from database
#     return render_template('albums.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html')

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
