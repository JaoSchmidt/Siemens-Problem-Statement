from api import app
from flask import render_template, send_file
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

    return render_template('/section2.html',
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

    return render_template('/section3.html', terms=terms)

@app.route('/section3DownloadFile')
def section3DownloadFile():
    
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    getFile = "SELECT THRID_ FROM ATTESTATION WHERE ID = %s;"

    input=['Gabriel']
    cursor.execute(getFile,input)
    data = cursor.fetchone()

    # return send_file()
