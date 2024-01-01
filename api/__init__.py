from flask import Flask, request, jsonify, render_template, redirect, url_for
import jwt
import mysql.connector
import random

app = Flask(__name__)

def row_to_dict(row, cursor_description):
    """
    Convert a row fetched using cursor.fetchone() to a dictionary.
    
    Parameters:
    - row: A row fetched using cursor.fetchone().
    - cursor_description: The cursor description obtained using cursor.description.
    
    Returns:
    - A dictionary where keys are column names and values are corresponding row values.
    """
    if row is None or cursor_description is None:
        return None

    column_names = [column[0] for column in cursor_description]
    return dict(zip(column_names, row))

import api.pdf_signer
import api.renderSections

app.secret_key = "jaojaojao"

DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

""" DATABASE_CONFIG = {
    "host":"db",
    "user": "test",
    "password": "password",
    "database": "attestation"
} """

@app.route('/')
def main():
    user = request.cookies.get('user')

    """ conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql ="SELECT * FROM USERS WHERE USERNAME = %s;"
    input=['Gabriel']
    cursor.execute(sql, input)
    data = cursor.fetchone() """

    if user:
        return redirect('dashboard')
    else :
        return render_template('login.html', users=user)


@app.route('/dashboard')
def dashboard():
    user = request.cookies.get('user')

    if user:
        return render_template('dashboard.html')
    else:
        return redirect('/')




# @param => { "password" => input } to encode
@app.route('/signup')
def encode():
    
    data = request.get_json()

    return jwt.encode(data, app.secret_key, algorithm='HS256')


def decode( data ):

    data = jwt.decode(data, app.secret_key, algorithms=['HS256'])
    return data["password"]

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
    
    if row is None:
        return {"code": "-1"}
    elif decode(row[2]) == input_password:
        return {"code": "1", "user": row[0]}
    else:
        return {"code": "0"}


###### API GET TEMPLATES
@app.route('/api/components/showProducts', methods=['GET'])
def showProducts():

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    res_data = []

    sql = "SELECT * FROM PRODUCT_VERSION GROUP BY PRODUCT_ID;"
    cursor.execute(sql)
    data = cursor.fetchall()

    getVersions = "SELECT VERSION_ID FROM PRODUCT_VERSION WHERE PRODUCT_ID = %s;"
    for p in data:
        params = [p[0]]
        cursor.execute(getVersions, params)
        versions = cursor.fetchall()

        versions_arr = []
        for v in versions:
            versions_arr.append(v)

        res_data.append( [p[0], versions_arr] )
        

    return render_template('/components/showProducts.html', products=res_data)

##### Get PPSSO products where ATTESTATION_ID IS NULL
@app.route('/api/getAttestationAlert', methods=['POST'])
def getAttestationAlert():

    data = request.get_json()
    user_id = data["data"].get('user_id')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    sql = """
    SELECT PRODUCT_ID, VERSION_ID FROM PRODUCT_VERSION PV
    LEFT JOIN PRODUCT_X_RESPONSIBLE_USER PXRU ON PXRU.FK_PRODUCTID_PXRU = PV.PRODUCT_ID
    WHERE PXRU.FK_USERID_PXRU = %s
    AND PXRU.IS_PPSSO = 1
    AND PV.FK_ATTESTATION_ID_PV IS NULL;
    """
    params=[user_id]
    cursor.execute(sql, params)
    res = cursor.fetchall()

    return render_template('/components/attestationAlert.html', attestations=res)


##### Attestation Form
@app.route('/api/components/chooseProduct', methods=['POST'])
def newAttestationForm():

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql = "SELECT PRODUCT_ID, VERSION_ID FROM PRODUCT_VERSION;"

    cursor.execute(sql)
    res = cursor.fetchall()

    return render_template('/components/newAttestationForm/chooseProduct.html', products=res)


@app.route('/api/checkProductsHasAttestation', methods=['POST'])
def checkProductsHasAttestation():
     
    data = request.get_json()
    products = data["data"].get('products')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    hasAttestation = []

    for p in products:
        splited = p.split('_')
        sql = "SELECT FK_ATTESTATION_ID_PV FROM PRODUCT_VERSION WHERE PRODUCT_ID = %s AND VERSION_ID = %s LIMIT 1;"
        params=[splited[0], splited[1]]
        cursor.execute(sql, params)

        res = cursor.fetchone()
        ## @return => INT || NULL, 1 ou null
        if res is not None and res[0] is not None:
            hasAttestation.append( [splited[0],splited[1]] )

    if len(hasAttestation) > 0:
        return { "array": hasAttestation, "code": "-1" }
    else:
        return { "code": "1" }

@app.route('/api/assignUser', methods=['POST'])
def assignUser():

    data = request.get_json()
    products = data["data"].get('products')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql = "SELECT USERNAME FROM USERS;"
    cursor.execute(sql)

    res = cursor.fetchall()

    return render_template('/components/newAttestationForm/assignUser.html', products=products, users=res)





##### Insert Attestation X Sections X Users Assigned
@app.route('/api/createAttestation', methods=['POST'])
def createAttestation():

    # Pd colocar filtro aqui depois para checar se cada section tem pelo menos 1 usuario

    data = request.get_json()
    products = data["data"].get('products')
    users = data["data"].get('users')

    s1_users = []
    s2_users = []
    s3_users = []
    for u in users:
        if u == "s1":
            for i in users["s1"]:
                s1_users.append(i)
        if u == "s2":
            for i in users["s2"]:
                s2_users.append(i)
        if u == "s3":
            for i in users["s3"]:
                s3_users.append(i)


    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    faults = []

    # Create Attestation
    new_id = random.randint(0,9)*random.randint(0,100)*random.randint(0,999)

    sql = "INSERT INTO ATTESTATION(ID, CREATED_AT) VALUES(%s, NOW());"
    params = [new_id]
    cursor.execute(sql, params)
    conn.commit()

    for u in s1_users :
        sql = "SELECT ID FROM USERS WHERE USERNAME = %s"
        params = [u]
        cursor.execute(sql, params)

        user_id = cursor.fetchone()[0]

        sql = """
        INSERT INTO ATTESTATION_X_FORM_SECTIONS( ATTESTATION_ID_AXFS, FORM_SECTION_ID_AXFS, USER_ID_AXFS )
        VALUES( %s, %s, %s )
        """
        params = [new_id,1,user_id]
        cursor.execute(sql, params)

    for u in s2_users:
        sql = "SELECT ID FROM USERS WHERE USERNAME = %s"
        params = [u]
        cursor.execute(sql, params)

        user_id = cursor.fetchone()[0]

        sql = """
        INSERT INTO ATTESTATION_X_FORM_SECTIONS( ATTESTATION_ID_AXFS, FORM_SECTION_ID_AXFS, USER_ID_AXFS )
        VALUES( %s, %s, %s )
        """
        params = [new_id,2,user_id]
        cursor.execute(sql, params)

    for u in s3_users:
        sql = "SELECT ID FROM USERS WHERE USERNAME = %s"
        params = [u]
        cursor.execute(sql, params)

        user_id = cursor.fetchone()[0]

        sql = """
        INSERT INTO ATTESTATION_X_FORM_SECTIONS( ATTESTATION_ID_AXFS, FORM_SECTION_ID_AXFS, USER_ID_AXFS )
        VALUES( %s, %s, %s )
        """
        params = [new_id,3,user_id]
        cursor.execute(sql, params)

    for p in products:
        splited = p.split('_')
        product_id = splited[0]
        version_id = splited[1]

        sql = """
        UPDATE PRODUCT_VERSION
        SET FK_ATTESTATION_ID_PV = %s
        WHERE PRODUCT_ID = %s
        AND VERSION_ID = %s
        """
        params = [new_id,product_id,version_id]
        cursor.execute(sql, params)
        conn.commit()

    return 'OK'

@app.route('/api/getUserIncompleteSections', methods=['POST'])
def getUserIncompleteSections():

    data = request.get_json()
    user_id = data["data"].get('user_id')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql = """
    SELECT PRODUCT_ID, VERSION_ID, ATTESTATION_ID_AXFS,FORM_SECTION_ID_AXFS FROM ATTESTATION_X_FORM_SECTIONS AXFS
    JOIN PRODUCT_VERSION PV ON PV.FK_ATTESTATION_ID_PV = AXFS.ATTESTATION_ID_AXFS
    WHERE USER_ID_AXFS = %s
    AND USER_COMPLETED = 0
    """
    params = [user_id]
    cursor.execute(sql, params)

    res = cursor.fetchall()

    return render_template('/components/incompleteSectionAlert.html', incompletes=res)
    

##### GET FORM TEMPLATES
@app.route('/api/getForm', methods=['POST'])
def getForm():

    data = request.get_json()
    return



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
    app.run(debug=True,host='0.0.0.0',port=5000,threaded=True)
