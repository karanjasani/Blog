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
                author = "Anonymous Coward"
                #return False
        else:
            author = "Anonymous Coward"
            #return False

    except sqlite3.Error as er:
        print(er)

    #author = "Anonymous Coward"
    return True


@app.route("/articles/<int:articleid>/addcomment", methods='POST')
@app.login_required
def addcomment(articleid):
    if (request.method == 'POST'):
        try:
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
                    c.execute("insert into comment (comment_content, email, article_id, create_time, update_time) values (?,?,?,?,?)",
                                    [details['comment_content'], email, details['articleid'],datetime.datetime.now(),datetime.datetime.now()])
                    db.commit()

                else:
                    c.execute("insert into comment (comment_content, email, article_id, create_time, update_time) values (?,?,?,?,?)",
                                    [details['comment_content'], author, details['articleid'],datetime.datetime.now(),datetime.datetime.now()])
                    db.commit()
                c.execute("select comment_id from comments order by update_time desc limit 1")
                row = c.fetchone()
                response = Response(status=201, mimetype='application/json')
                response.headers['location'] = 'http://127.0.0.1:5000/articles/'+str(details['articleid'])+'/comments/'+str(row[0])

            else:
                response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response

@app.route("articles/<int:articleid>/comments/countcomment", methods='GET')
def countcomment(articleid):
    try:
        db = get_db()
        c = db.cursor()

        c.execute("select count(*) from comment where article_id=(:articleid)",{"articleid":articleid})
        comment_count = c.fetchone()
        message = {
            "Number of comments :": comment_count,
        }
    except sqlite3.Error as er:
            print(er)

    return jsonify(message)

@app.route("/deletecomment", methods='DELETE')
@app.login_required
def deletecomment():
    try:
        db = get_db()
        c = db.cursor()
        commentid = request.args.get('commentid')
        email = request.authorization.username

        c.execute("delete from comment where email=(:email) and comment_id=(:commentid)", {"email":email,"commentid":commentid})
        if (c.rowcount == 1):
            db.commit()
            response = Response(status=200, mimetype='application/json')
        else:
            response = Response(status=404, mimetype='application/json')
    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')
    return response

@app.route("/articles/<int:articleid>/comments/recentcomments", methods='DELETE')
@app.login_required
def recentcomments(articleid):
    try:
        db = get_db()
        c = db.cursor()
        db.row_factory = dict_factory
        recent = request.args.get('recent')

        c.execute("select comment_content from comment where article_id=(:articleid) order by update_time desc limit (:recent)", {"articleid":articleid, "recent":recent})
        recent_comments = c.fetchall()
        recent_comments_length = len(recent_comments)
        return jsonify(recent_comments)
        if(recent_comments_length == 0):
            response = Response(status=404, mimetype='application/json')

    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response
