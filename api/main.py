from flask import Flask, request, jsonify, render_template
# import mysql.connector

app = Flask(__name__)


DATABASE_CONFIG = {
    "host":"db",
    "user": "the_user",
    "passowrd": "the_password",
    "database": "attestation"
}

@app.route('/')
def main():
    return render_template('./form.html')

# @app.route('/submit_form', methods=['POST'])
# def submit_form():
#     try:
#         data = request.get_json()

#         product_name = data.get('product_name')
#         version_number = data.get('version_number')
#         responsible_person = data.get('responsible_person')

#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()

#         # ... (perform database operations as in the previous example)
#         print(product_name)
#         print(version_number)
#         print(responsible_person)

#         connection.commit()
#         connection.close()

#         return jsonify({"message": "Form submitted successfully!","product":product_name}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error submitting form: {str(e)}"}), 500

# @app.route('/get_form', methods=['GET'])
# def get_form():
#     try:
#         connection = mysql.connector.connect(**DATABASE_CONFIG)
#         cursor = connection.cursor()

#         # Retrieve form data from the database
#         cursor.execute("SELECT ProductName, VersionNumber, ResponsiblePerson FROM AttestationForm")
#         forms = [{"product_name": row[0], "version_number": row[1], "responsible_person": row[2]} for row in cursor.fetchall()]

#         connection.close()

#         return jsonify({"forms": forms}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error retrieving form data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
