import sys

from flask import Flask, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import jwt
import mysql.connector


app = Flask(__name__)
app.secret_key = "some_private_key"

# DATABASE_CONFIG = {
#     "host":"srv881.hstgr.io",
#     "user": "u138282597_jao",
#     "password": "bananasplitBA$$22",
#     "database": "u138282597_siemens"
# }
DATABASE_CONFIG = {
    "host":"db",
    "user": "test",
    "password": "password",
    "database": "attestation"
}

def get_db():
    return mysql.connector.connect(**DATABASE_CONFIG)

def generate_token(user_id):
    try:
        payload = {'user_id':user_id}
        return jwt.encode(payload,app.secret_key,algorithm='HS256')
    except Exception as e:
        return e

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    input_username = data["data"].get('username')
    input_password = data["data"].get('password')

    conn = get_db()
    cursor = conn.cursor()

    sql ="SELECT * FROM USERS WHERE USERNAME = %s LIMIT = 1;"
    input=[input_username]
    cursor.execute(sql, input)
    row = cursor.fetchone()
    while row is not None:
        row = cursor.fetchone()


    if row:
        token = generate_token(row[0])
        return jsonify({'token':token,'user_id':row[0],'username':row[1]}),200
    else:
        er = 'Invalid login credentials'
        return jsonify({'error':er}),401

@app.route('/dashboard')
def dashboard():
    token = request.headers.get('Authorization')

    if not token:
        er = 'Token missing'
        return jsonify({'error':er}),401
    
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = payload.get('user_id')

        conn = get_db()
        cursor = conn.cursor()

        # Your logic to fetch user data goes here (e.g., from the database)
        user_data = {'user_id': user_id, 'username': ''}
        return jsonify(user_data), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


###### API FETCH
# @app.route('/api/checkUser', methods=['POST'])
# def checkUser():
#     
#     data = request.get_json()

#     input_username = data["data"].get('username')
#     input_password = data["data"].get('pass')

#     conn = mysql.connector.connect(**DATABASE_CONFIG)
#     cursor = conn.cursor()

#     sql ="SELECT * FROM USERS WHERE USERNAME = %s LIMIT 1;"
#     params=[input_username]
#     cursor.execute(sql, params)
#     row = cursor.fetchone()
#     
#     if row[2] == input_password:
#         return render_template(url_for('dashboard'))
#     else:
#         return {"code": "-1"}


""" @app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()

        product_name = data.get('product_name')
        version_number = data.get('version_number')
        responsible_person = data.get('responsible_person')

        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        # ... (perform database operations as in the previous example)
        print(product_name)
        print(version_number)
        print(responsible_person)

        connection.commit()
        connection.close()

        return jsonify({"message": "Form submitted successfully!","product":product_name}), 200

    except Exception as e:
        return jsonify({"error": f"Error submitting form: {str(e)}"}), 500

@app.route('/get_form', methods=['GET'])
def get_form():
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        # Retrieve form data from the database
        cursor.execute("SELECT ProductName, VersionNumber, ResponsiblePerson FROM AttestationForm")
        forms = [{"product_name": row[0], "version_number": row[1], "responsible_person": row[2]} for row in cursor.fetchall()]

        connection.close()

        return jsonify({"forms": forms}), 200

    except Exception as e:
        return jsonify({"error": f"Error retrieving form data: {str(e)}"}), 500 """

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
