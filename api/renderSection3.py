from xhtml2pdf import pisa             # import python module
import io
import os
import sys
from api import app,row_to_dict
from flask import render_template, send_file, request, send_from_directory
import mysql.connector

from api.pdf_signer import createSignedPdf

DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

@app.route('/api/getAttestationPDF',methods=['GET','POST'])
def getAttestationPDF():
    data = request.get_json()
    print(data,sys.stdout)
    attestation_id = data.get('attestation_id')

    pdf_binary, filename = fetchPdf(attestation_id)

    pdf_file = io.BytesIO(pdf_binary)

    print(filename,sys.stdout)
    return send_file(pdf_file,mimetype='application/pdf',as_attachment=True,download_name=filename)
    # return send_from_directory(os.path.dirname(filename),os.path.basename(filename),as_attachment=True)

def fetchPdf(attestation_id):
    sql = "SELECT PDF,FILENAME FROM ATTESTATION WHERE ID = %s"
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    cursor.execute(sql, (attestation_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        pdf_binary, filename = result
        return pdf_binary, filename
    else:
        return b''


def placePdfOnDatabase(attestation_id,pdf_path):
    sql = """
    UPDATE ATTESTATION SET
        PDF = %s,
        FILENAME = %s
    WHERE ID = %s
    """
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    with open(pdf_path, 'rb') as file:
        pdf_binary = file.read()

    # Prepare the parameters for the SQL query
    params = (pdf_binary,pdf_path, attestation_id)

    cursor.execute(sql, params)
    conn.commit()
    return 'OK'

def generateAttestationPDF(attestation_id):

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    sql = """
    SELECT PRODUCT_ID, VERSION_ID, RELEASE_PUBLISH_DATE
    FROM PRODUCT_VERSION
    WHERE FK_ATTESTATION_ID_PV = %s
    """
    params = [attestation_id]
    cursor.execute(sql, params)

    products = cursor.fetchall()

    sql = """
    SELECT * FROM ATTESTATION A
    JOIN PRODUCT_VERSION PV ON PV.FK_ATTESTATION_ID_PV = A.ID
    WHERE ID = %s
    LIMIT 1
    """
    params = [attestation_id]
    cursor.execute(sql, params)

    res = cursor.fetchone()

    cookie_user_id = request.cookies.get('user')
    sql ="SELECT * FROM USERS WHERE ID = %s LIMIT 1;"
    print(cookie_user_id,sys.stdout)
    params=[cookie_user_id]
    cursor.execute(sql,params)
    fetch = cursor.fetchone()
    user = row_to_dict(fetch,cursor.description)

    attestation_date = res[18].strftime('%Y-%m-%d')
    title = f"SIEMENS_{products[0][0]}_{products[0][1]}_{attestation_date}"
    
    rendered_template = render_template('/engine/attestationModelRedone.html', data=res, products=products)
    result_file = open(f"./api/resources/attestationsPdfs/{title}.pdf", "w+b")

    # # convert HTML to PDF
    pisa.CreatePDF(
            rendered_template,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()

    code = createSignedPdf(user.get('USERNAME'),int(user.get('ID')),f"./api/resources/attestationsPdfs/{title}.pdf")
    if(code["code"] == "0"):
        placePdfOnDatabase(attestation_id,f"./api/resources/attestationsPdfs/{title}_signed.pdf")
    return 'OK'
    # return pisa_status.err


@app.route('/api/submitSection3ThirdParty')
def submitSection3ThirdParty():
    data = request.get_json()
    user_id = request.cookies.get('user')
    section_id = data["data"].get('section_id')
    attestation_id = data["data"].get('attestation_id')

    thirdPartyTerms = data["data"].get('thirdPartyTerms')
    thirdPartyfile = data["data"].get('thirdPartyfile')

    sql = """
    UPDATE ATTESTATION SET
        THRID_PARTY_TERMS = %s,
        THRID_PARTY_FILE = %s,
    WHERE ID = %s
    """
    params = [
        thirdPartyTerms,
        thirdPartyfile,
        attestation_id
    ]

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
        return str(err.msg)
    
    generateAttestationPDF()


    return 'OK'

@app.route('/api/submitSection3', methods=['POST'])
def submitSection3():
    data = request.get_json()
    user_id = request.cookies.get('user')
    section_id = data["data"].get('section_id')
    attestation_id = data["data"].get('attestation_id')

    acceptTerms = data["data"].get('acceptTerms')

    sql = """
    UPDATE ATTESTATION SET
        SIGNATURE_TERMS = %s
    WHERE ID = %s
    """
    params = [
        acceptTerms,
        attestation_id
    ]

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

        generateAttestationPDF(attestation_id)
    except mysql.connector.Error as err:
        conn.rollback()
        return str(err.msg)
    return 'OK'

@app.route('/api/section3DownloadFile')
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

def section3(section_id, attestation_id):
    terms = {
        "acceptedTerms": "0",
        "signature": "asefioeur09",
        "thirdPartyTerms": "0",
        "file": None,
        }

    return render_template('/components/newAttestationForm/sections/section3.html', 
                           terms=terms,
                           section_id=section_id,
                           attestation_id=attestation_id
                           )


