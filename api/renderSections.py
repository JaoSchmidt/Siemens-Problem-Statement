import io
from api import app
from flask import render_template, send_file, request
import mysql.connector


DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

@app.route('/section2')
def section2():

    # data = request.get_json()
    # products = data["data"].get('products')

    softwareProducerInfo = {
        "companyName": "Weyland-Yutani Corp",
        "address": "Mars",
        "city":"Gotham",
        "stateProvince":"Bavaria",
        "postalCode":24604,
        "country":"Bin Chilling",
        "email":"weylandyutani.corp"
        }

    primaryContactInfo = {
        "name":"Yor Briar",
        "title":"Thorn Princess",
        "contactAddress":"westalis",
        "phoneNumber":666,
        "email":"thorn@strix.org",
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

