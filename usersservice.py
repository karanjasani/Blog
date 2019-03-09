from flask import Flask, jsonify, request, make_response
import sqlite3
from flask_api import status
import datetime
from http import HTTPStatus
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route("/create", methods=['POST'])
def createuser():
    if (request.method == 'POST'):
        details = request.get_json()

        conn = sqlite3.connect('blogdatabase.db')
        c = conn.cursor()
        update_time = datetime.datetime.now()
        c.execute("insert into users (name, email, password, create_time, update_time) values (?,?,?,?,?)",
                    [details['name'], details['email'], details['password'], update_time, update_time ])
        conn.commit()
        conn.close()

    else:
        return jsonify("enter valid details")

    message = {
        'status': 201,
        'message': 'Created: ' + request.url,
    }
    #response = jsonify(message)
    #response.status_code = status.HTTP_201_CREATED
    #response status_code
    #error handling
    #password hashing

    return make_response(jsonify({'error': 'Not found'}), 201)

@app.route("/login", methods=['POST'])
def loginuser():
    auth = request.authorization

    username = auth.username
    password = auth.password

    print(auth.username + "---")
    print(auth.password + "---")

    return

@auth.verify_password
def verify(username, password):
    print(username + "***")
    print(password + "***")
    return False

@app.route("/display", methods=['GET'])
@auth.login_required
def display():
    return {"meaning_of_life": 42}

if __name__ == '__main__':
    app.run(debug=True)
