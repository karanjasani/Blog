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
                return False
        else:
            message = {
                'status': 201,
                'mesg': 'User does not match: ' + request.url,
            }
            print(message)
            return False

    except sqlite3.Error as er:
        print(er)

    return False


@app.route("/postarticle", methods=['POST'])
@auth.login_required
def postarticle():
    if (request.method == 'POST'):
        db = get_db()
        c = db.cursor()
        details = request.get_json()
        update_time = datetime.datetime.now()
        email = request.authorization.username

        try:
            #c.execute("select email from users where email=(:email)", {'email':email})
            #row = c.fetchone()
            #if row is not None:
            #userid = row[0]
            c.execute("insert into article (title, content, email, create_time, update_time) values (?,?,?,?,?)",
                        [details['title'], details['content'], email, update_time, update_time ])
            db.commit()
            message = {
                'status': 201,
                'message': 'Article Posted: ' + request.url,
            }
            '''
            else:
                message = {
                    'status': 201,
                    'message': 'User or Password does not match ' + request.url,
                }
            '''
        except sqlite3.Error as er:
                print(er)

        return jsonify(message)

@app.route("/getarticle", methods=['GET'])
def getarticle():
    if (request.method == 'GET'):
        db = get_db()
        c = db.cursor()
        message = {}
        id = request.args.get('id')
        try:
            c.execute("select article_id, title, content, email, create_time, update_time from article where article_id=(:articleid)",{'articleid':id})
            row = c.fetchone()
            if row is not None:
                message = {
                    'Article id': row[0],
                    'Title': row[1],
                    'Content': row[2],
                    'User id': row[3],
                    'create time': row[4],
                    'Update time' : row[5],
                }
            else:
                message = {
                    'message':'article does not exists'
                }
        except sqlite3.Error as er:
                print(er)

    return jsonify(message)


@app.route("/editarticle", methods=['POST'])
@auth.login_required
def editarticle():
    if (request.method == 'POST'):
        db = get_db()
        c = db.cursor()
        id = request.args.get('id')
        email = request.authorization.username
        details = request.get_json()
        #update_time = datetime.datetime.now()
        message = {}
        try:
            for x in details:
                sql = "update article set "+x+"=(:key), update_time=(:updatetime) where article_id=(:id) and email=(:email)"
                c.execute(sql, {"key":details[x],"updatetime":datetime.datetime.now(), "id":id, "email":email})
                if (c.rowcount == 1):
                    db.commit()
                    message = {
                        'message':'article updated'
                    }
                else:
                    message = {
                        'message':'article not found for that user'
                    }

        except sqlite3.Error as er:
                print(er)

    return jsonify(message)



@app.route("/deletearticle", methods=['GET'])
@auth.login_required
def deletearticle():
    if (request.method == 'GET'):
        db = get_db()
        c = db.cursor()
        message = {}
        id = request.args.get('id')
        email = request.authorization.username

        try:
            c.execute("delete from article where article_id=(:articleid) and email=(:email)",{"email":email,"articleid":id})
            db.commit()
            if (c.rowcount == 1):
                db.commit()
                message = {
                    'message':'article deleted'
                }
            else:
                message = {
                    'message':'Article not found for that user'
                }
        except sqlite3.Error as er:
                print(er)

    return jsonify(message)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route("/retriverecentarticle", methods=['GET'])
def retriverecentarticle():
    db = get_db()
    db.row_factory = dict_factory
    c = db.cursor()
    message = {}
    recent = request.args.get('recent')

    try:
        c.execute("select * from article order by create_time desc limit (:recent)", {"recent":recent})
        recent_articles = c.fetchall()
        recent_articles_length = len(recent_articles)

        if(recent_articles_length == 0):
            recent_articles = {
                'message':'No articles found'
            }

    except sqlite3.Error as er:
            print(er)

    return jsonify(recent_articles)




if __name__ == '__main__':
    app.run(debug=True)
