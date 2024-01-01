from OpenSSL import crypto
import os
import sys
import mysql.connector
from pyhanko.sign.fields import append_signature_field
from pyhanko.sign import signers 
from pyhanko import stamp
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.sign.signers import SimpleSigner
from api import app, row_to_dict
from flask import request

DATABASE_CONFIG = {
    "host":"srv881.hstgr.io",
    "user": "u138282597_jao",
    "password": "bananasplitBA$$22",
    "database": "u138282597_siemens"
}

@app.route("/signpdf")
def signpdf():


    data = request.get_json()
    attestation_id = data["data"].get('attestation_id')

    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    cookie_user_id = request.cookies.get('user')
    sql ="SELECT * FROM USERS WHERE USERNAME = %s LIMIT 1;"
    params=[cookie_user_id]
    cursor.execute(sql,params)
    fetch = cursor.fetchone()
    user = row_to_dict(fetch,cursor.description)

    sql = "SELECT FILENAME FROM ATTESTATION WHERE ID = %s;"
    params=[attestation_id]
    cursor.execute(sql, params)
    fetch = cursor.fetchone()

    att = row_to_dict(fetch,cursor.description)
    if(att != None and user != None):
        print(user, file=sys.stderr)
        print(att, file=sys.stderr)
        createSignedPdf(user.USERNAME,user.ID,att.FILENAME)
    return {"code":"0"}

# https://pyhanko.readthedocs.io/en/latest/lib-guide/signing.html#text-based-stamps
def createSignedPdf(keyholder_name,serial_number,input_path):

    cs12path = "./resources/container.pfx"
    create_keys(keyholder_name,serial_number,cs12path)

    def sanity_check(x1, y1, w, h):
        x2 = x1 + w
        y2 = y1 + h
        return (x1, y1, x2, y2)

    cms_signer = signers.SimpleSigner.load_pkcs12(cs12path)
    with open(input_path, 'rb') as inf:
        w = IncrementalPdfFileWriter(inf)
        append_signature_field(
            w, sig_field_spec=SigFieldSpec(
                'Signature', box=sanity_check(250,50,300,80)
            )
        )
        meta = signers.PdfSignatureMetadata(field_name='Signature')
        if(cms_signer is not None):
            pdf_signer = signers.PdfSigner(
                meta, signer=cms_signer, stamp_style=stamp.TextStampStyle(
                    stamp_text='   Signed by: %(signer)s\n\t                Time: %(ts)s',
                    background=images.PdfImage('./resources/siemens_logo.png'),
                    text_box_style=text.TextBoxStyle(
                        font_size=13,
                        font=opentype.GlyphAccumulatorFactory('./resources/NotoSans-Regular.ttf')
                    ),
                )
            )
            with open(input_path.replace(".pdf","")+"_signed.pdf", 'wb') as outf:
                pdf_signer.sign_pdf(w, output=outf)
            os.remove('./resources/container.pfx')
            return { "code":"0"}
        else:
            return { "code":"1"}


def createKeyPair(type, bits):
    """
    Create a public/private key pair
    Arguments: Type - Key Type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key (1024 or 2048 or 4096)
    Returns: The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey

def create_self_signed_cert(pKey,subject_name,serial_number,years_to_expire=10):
    """Create a self signed certificate. This certificate will not require to be signed by a Certificate Authority."""
    # Create a self signed certificate
    cert = crypto.X509()
    # Common Name (e.g. server FQDN or Your Name)
    cert.get_subject().CN = subject_name
    # Serial Number
    # cert.set_serial_number(int(time.time() * 10))
    cert.set_serial_number(int(serial_number))
    # Not Before
    cert.gmtime_adj_notBefore(0)  # Not before
    # Not After (Expire after 10 years)
    cert.gmtime_adj_notAfter(years_to_expire * 365 * 24 * 60 * 60)
    # Identify issue
    cert.set_issuer((cert.get_subject()))
    cert.set_pubkey(pKey)
    cert.sign(pKey, 'md5')  # or cert.sign(pKey, 'sha256')
    return cert

def create_keys(keyholder_name,serial_number,output_path,years_to_expire=10):
    """Generate the certificate"""
    summary = {}
    summary['OpenSSL Version'] = '23.0.1'
    # Generating a Private Key...
    key = createKeyPair(crypto.TYPE_RSA, 1024)
    # PEM encoded
    # with open('./resources/private_key.pem', 'wb') as pk:
    #     pk_str = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
    #     pk.write(pk_str)
    #     summary['Private Key'] = pk_str
    # Done - Generating a private key...
    # Generating a self-signed client certification...
    cert = create_self_signed_cert(key,keyholder_name,serial_number,years_to_expire)
    # with open('./resources/certificate.cer', 'wb') as cer:
    #     cer_str = crypto.dump_certificate(
    #         crypto.FILETYPE_PEM, cert)
    #     cer.write(cer_str)
    #     summary['Self Signed Certificate'] = cer_str

    # Take a private key and a certificate and combine them into a PKCS12 file.
    # Generating a container file of the private key and the certificate...
    p12 = crypto.PKCS12()
    p12.set_privatekey(key)
    p12.set_certificate(cert)
    open(output_path, 'wb').write(p12.export())
    # You may convert a PKSC12 file (.pfx) to a PEM format
    # Done - Generating a container file of the private key and the certificate...
    # To Display A Summary
    # print("## Initialization Summary ##################################################")
    # print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    # print("############################################################################")


