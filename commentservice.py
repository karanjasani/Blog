from flask import Flask, jsonify, request, make_response, g
import sqlite3
from flask_api import status
import datetime
from http import HTTPStatus
from flask_httpauth import HTTPBasicAuth
from passlib.hash import sha256_crypt

app = Flask(__name__)
auth = HTTPBasicAuth()

DATABASE = 'blogdatabase.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        print("database closed")
        db.close()

@auth.verify_password
def verify(username, password):
    print("inside verify")
    db = get_db()
    c = db.cursor()
    message = {}
    global author = ""
    try:
        c.execute("select password from users where email=(:email)", {'email':username})
        row = c.fetchone()
        if row is not None:
            p = row[0]
            print(p)
            if (sha256_crypt.verify(password,p)):
                return True
            else:
                message = {
                    'status': 201,
                    'mesg': 'Password does not match: ' + request.url,
                }
                print(message)
                author = "Anonymous Coward"
                return False
        else:
            message = {
                'status': 201,
                'mesg': 'User does not match: ' + request.url,
            }
            print(message)
            author = "Anonymous Coward"
            return False

    except sqlite3.Error as er:
        print(er)

    author = "Anonymous Coward"
    return False


@app.route("/addcomment", methods='POST')
@app.login_required
def addcomment():
    if (request.method == 'POST'):
        db = get_db()
        c = db.cursor()
        details = request.get_json()
        email = request.authorization.username
        update_time = datetime.datetime.now()

        c.execute("select * from article where article_id=(:articleid)", {'articleid':articleid})
        articles = c.fetchall()
        articles_length = len(articles)
        if (articles_length == 1):
            if (author == ""):
                c.execute("insert into comment (comment_content, email, article_id, create_time, update_time) values (?,?,?,?,?)", [details['comment_content'], author, details['articleid'],datetime.datetime.now(),datetime.datetime.now()])
                db.commit()
            else:
                c.execute("insert into comment (comment_content, email, article_id, create_time, update_time) values (?,?,?,?,?)", [details['comment_content'], email, details['articleid'],datetime.datetime.now(),datetime.datetime.now()])
                db.commit()
            message = {
                'status': 201,
                'message': 'Comment Posted: ' + request.url,
            }
        else:
            message = {
                'status': 201,
                'message': 'Article does not exists: ' + request.url,
            }


    except sqlite3.Error as er:
            print(er)

    return jsonify(message)

@app.route("/countcomment", methods='POST')
@app.login_required
def countcomment():
    db = get_db()
    c = db.cursor() 
    id = request.args.get('id')

    try:
        c.execute("select count(*) from comment where article_id=(:articleid)",{"articleid":id})
        comment_count = c.fetchone()
        message = {
            "Number of comments :": comment_count,
        }
    except sqlite3.Error as er:
            print(er)

    return jsonify(message)
