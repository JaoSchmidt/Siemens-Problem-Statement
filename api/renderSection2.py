from xhtml2pdf import pisa             # import python module
import io
import sys
from api import app
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

def section2(section_id, attestation_id):


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
        "email":"thorn@strix.org",
        }

    return render_template('/components/newAttestationForm/sections/section2.html',
                           form1=softwareProducerInfo,
                           form2=primaryContactInfo,
                           section_id=section_id,
                           attestation_id=attestation_id
                           )

@app.route('/api/submitSection2',methods=['POST'])
def submitSection2():
    # Pd colocar filtro aqui depois para checar se cada section tem pelo menos 1 usuario

    data = request.get_json()
    attestation_id = data["data"].get('attestation_id')
    section_id = data["data"].get('section_id')
    user_id = request.cookies.get('user')

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
    UPDATE ATTESTATION SET
        COMPANY_NAME = "%s",
        ADDRESS = "%s",
        CITY = "%s",
        STATE_OR_PROVINCE = "%s",
        POSTAL_CODE = %s,
        COUNTRY = "%s",
        COMPANY_WEBSITE = "%s",
        NAME = "%s",
        TITLE = "%s",
        CONTACT_ADDRESS = "%s",
        PHONE_NUMBER = %s,
        EMAIL = "%s"
    WHERE ID = %s
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
        attestation_id
    ]
    print(params,sys.stdout)

    none_indexes = [index for index, value in enumerate(params) if value is None]
    if len(none_indexes) > 0:
        return f'ERROR indexes {none_indexes} are Null'

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()

        sql = """
        UPDATE ATTESTATION_X_FORM_SECTIONS
        SET USER_COMPLETED = 1
        WHERE ATTESTATION_ID_AXFS = %s
        AND FORM_SECTION_ID_AXFS = %s
        AND USER_ID_AXFS = %s
        """
        params = [attestation_id, section_id, user_id]
        cursor.execute(sql, params)
        conn.commit()

    except mysql.connector.Error as err:
        conn.rollback()
        return err.msg
    return 'OK'
