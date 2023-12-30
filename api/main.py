import sys
from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
#import hashlib

app = Flask(__name__)



DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

@app.route('/')
def main():
    token = request.cookies.get('token')

    """ conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql ="SELECT * FROM USERS WHERE USERNAME = %s;"
    input=['Gabriel']
    cursor.execute(sql, input)
    data = cursor.fetchone() """

    if token:
        return redirect('dashboard')
    else :
        return render_template('login.html', users=token)


@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('token')

    if token:
        return render_template('dashboard.html')
    else:
        return redirect('/')



###### API FETCH
@app.route('/api/checkUser', methods=['POST'])
def checkUser():
    
    data = request.get_json()

    input_username = data["data"].get('username')
    input_password = data["data"].get('pass')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql ="SELECT * FROM USERS WHERE USERNAME = %s LIMIT 1;"
    params=[input_username]
    cursor.execute(sql, params)
    row = cursor.fetchone()
    
    if len(row) == 0:
        return {"code": "-1"}
    elif row[2] == input_password:
        isUserLogged = True
        return {"code": "1"}
    else:
        return {"code": "0"}


###### API GET TEMPLATES
@app.route('/api/components/showProducts', methods=['GET'])
def showProducts():

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql ="SELECT * FROM PRODUCT_VERSION;"
    cursor.execute(sql)
    data = cursor.fetchall()

    return render_template('/components/showProducts.html', products=data)

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
