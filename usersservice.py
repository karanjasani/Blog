from flask import Flask, jsonify, request, make_response, g
import sqlite3, json
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

@app.route("/create", methods=['POST'])
def createuser():
    if (request.method == 'POST'):
        details = request.get_json()
        db = get_db()
        c = db.cursor()
        update_time = datetime.datetime.now()
        try:
            password = sha256_crypt.encrypt((str(details['password'])))
            c.execute("insert into users (name, email, password, create_time, update_time) values (?,?,?,?,?)",
                    [details['name'], details['email'], password, update_time, update_time ])
            db.commit()

            message = {
                'status': 201,
                'message': 'Created: ' + request.url,
            }
        except sqlite3.Error as er:
            print(er)
            return jsonify({'Error Message': 'Conflict'}), 409

    return jsonify(message)

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

@app.route("/display", methods=['POST'])
def display():
    db = get_db()
    c = db.cursor()
    message = {}
    c.execute("select name, email from users")
    row = c.fetchall()

    #row = c.execute("select * from users")
    '''
    message = {
        'status': 201,
        'test': 'works fine: ' + request.url,
    }
    '''

    return jsonify(row)

@app.route("/deleteuser", methods=['POST'])
@auth.login_required
def deleteuser():
    db = get_db()
    c = db.cursor()
    message = {}
    print("Inside delete user function")
    details = request.get_json()
    email = request.authorization.username
    try:
        c.execute("delete from users where email=(:email)",{'email':details['email']})
        db.commit()
        print("Record deleted")
        message = {
            'status': 201,
            'mesg': 'User Deleted: ' + request.url,
        }

    except sqlite3.Error as er:
            print(er)

    return jsonify(message)

@app.route("/updatepassword", methods=['POST'])
@auth.login_required
def updatepassword():
    db = get_db()
    c = db.cursor()
    print("inside update password")
    details = request.get_json()
    new_password = sha256_crypt.encrypt((str(details['new_password'])))
    message = {}
    email = request.authorization.username
    update_time = datetime.datetime.now()
    try:
        c.execute("update users set password=(:password), update_time=(:updatetime) where email=(:email)",{'email':email, 'password':new_password, 'updatetime':update_time})
        db.commit()
        print("password updated")
        message = {
            'status': 201,
            'message': 'Password Updated: ' + request.url,
        }

    except sqlite3.Error as er:
        print(er)

    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)
