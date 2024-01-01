import io
import sys
from api import app, row_to_dict
from flask import render_template, send_file, request
import mysql.connector


DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

# find other example os completed databases and take a history of its columns
def exploreOldAttestations(product_id):
    
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # get all possible old attestations of a specific product
    otherProductAttestastions = """SELECT FK_ATTESTATION_ID_PV FROM PRODUCT_VERSION 
        WHERE PRODUCT_ID = %s AND FK_ATTESTATION_ID_PV is NOT NULL"""
    input=[product_id]
    cursor.execute(otherProductAttestastions,input)
    rows = cursor.fetchall()
    attestations = [attestation for row in rows for attestation in row]

    # get all old attestations that are completed
    allAtestationsSQL = f"SELECT * FROM ATTESTATION WHERE id IN ({', '.join(['%s' for _ in attestations])})"
    cursor.execute(allAtestationsSQL,attestations)
    tupleList = cursor.fetchall()


    if tupleList is not None:
        firstNonNull = []*8
        print(len(tupleList),sys.stdout)
        print(len(firstNonNull),sys.stdout)
        for tuple_item in reversed(tupleList):
            for i, value in enumerate(tuple_item):
                if value is not None and firstNonNull[i] is None:
                    firstNonNull[i] = value
        return { "code": "0", "data":firstNonNull}       
    else:
        return { "code": "-1" }

@app.route('/section2',methods=['GET'])
def section2():

    
    # data = request.get_json()
    # product_id = data["data"].get('product_id')
    # data = request.get_json()

    # attestation_id = data["data"].get('attestation_id')

    # conn = mysql.connector.connect(**DATABASE_CONFIG)
    # cursor = conn.cursor()

    # getFile = "SELECT * FROM ATTESTATION WHERE ID = %s;"

    # input=[attestation_id]
    # cursor.execute(getFile,input)

    softwareProducerInfo = {
        "companyName": "Weyland-Yutani Corp",
        "address": "Mars",
        "city":"Gotham",
        "stateProvince":"Bavaria",
        "postalCode":24604,
        "country":"Bin Chilling",
        "website":"weylandyutani.corp"
        }

    primaryContactInfo = {
        "name":"Yor Briar",
        "title":"Thorn Princess",
        "contactAddress":"westalis",
        "phoneNumber":666,
        "website":"thorn@strix.org",
        }

    return render_template('/components/newAttestationForm/sections/section2.html',
                           form1=softwareProducerInfo,
                           form2=primaryContactInfo)

@app.route('/section3')
def section3():
    terms = {
        "acceptedTerms": True,
        "signature": "asefioeur09",
        "thirdPartyTerms": False,
        "file": None,
        }

    return render_template('/components/newAttestationForm/sections/section3.html', terms=terms)

@app.route('/section3DownloadFile')
def section3DownloadFile():
    data = request.get_json()

    attestation_id = data["data"].get('attestation_id')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    getFile = "SELECT THRID_PARTY_FILE FROM ATTESTATION WHERE ID = %s;"

    input=[attestation_id]
    cursor.execute(getFile,input)

    data = cursor.fetchone()
    file_like_data = io.BytesIO(data[0])
    return send_file(file_like_data)

@app.route('/submitSection2',methods=['POST'])
def submitSection2():
    # Pd colocar filtro aqui depois para checar se cada section tem pelo menos 1 usuario

    data = request.get_json()
    companyName = data["data"].get('companyName')
    address = data["data"].get('address')
    city = data["data"].get('city')
    stateProvince = data["data"].get('stateProvince')
    postalCode = data["data"].get('postalCode')
    country = data["data"].get('country')
    website = data["data"].get('website')
    name = data["data"].get('name')
    title = data["data"].get('title')
    contactAddress = data["data"].get('contactAddress')
    phoneNumber = data["data"].get('phoneNumber')
    email = data["data"].get('email')
 
    sql = """
    INSERT INTO ATTESTATION (
        COMPANY_NAME,
        ADDRESS,
        CITY,
        STATE_OR_PROVINCE,
        POSTAL_CODE,
        COUNTRY,
        COMPANY_WEBSITE,
        NAME,
        TITLE,
        CONTACT_ADDRESS,
        PHONE_NUMBER,
        EMAIL,
        )
        VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
    """
    params = [
        companyName,
        address,
        city,
        stateProvince,
        postalCode,
        country,
        website,
        name,
        title,
        contactAddress,
        phoneNumber,
        email,
    ]

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
    except mysql.connector.Error as err:
        conn.rollback()
        return 'ERROR'
    return 'OK'
