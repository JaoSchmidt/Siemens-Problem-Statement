# Siemens-Problem-Statement
 End of the year problem statement sent by Siemens to create a automatic form. 
 

 ## Installing

```
pip install -e .
```

## Development
To run the app:
```
flask --app api run --host=0.0.0.0 --debug
```

## Siemens problem solution proposal
General proposal is to create a system capable of both detecting the new software versions and allowing the manual insertion of it.
The system will then be able to make every use case required in the problem statment.

A simple prototype was build in Flask. [Here is an example of signed pdf](https://github.com/JaoSchmidt/Siemens-Problem-Statement/blob/main/api/resources/attestationsPdfs/SIEMENS_FLA5120N12_2B_2024-01-01_signed.pdf)

#### 1. Creating the capability to register a trigger request for Self Attestation form
To register a "trigger" for the Self Attestation form, that is, to insert a new software version which will require a Self Attestation Form. 

The solution for that isn't actually built inside the flask prototype, because it would need a modification of the CI/CD script of the target repo.

``` bash
# assuming there is a tag name, take the leftest number (the major version)
MAJOR_VERSION=$(echo "${{ github.event.release.tag_name }}" | grep -oP '^\d+')
# if not there will need to be another way

# send to the database
mysql --user=sysadmin --password=mypassword \
-e "INSERT IGNORE INTO PRODUCT_VERSION (PRODUCT_ID,VERSION_ID) VALUES ("This is the product name",$MAJOR_VERSION);"
```
In the target repo, here is what this code does:
1. Takes the major version of the software
2. Insert its version in the database if possible

Doing this will insert a product to be attested, as well as its major version, as required in the CISA document.

#### 2. Match if there is already an existing attestation for the product+version number already existing
The prototype checks if there is a completed attestation for the same product+version before allowing the trigger. 
In the API this is a made with a simple condition inside the sql.

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/096b325b-a6d5-4b6e-9e77-b1d9c2ce474c)

In the image, the attempt to trigger a flow of an already existing code causes an error

Additionally, it is also used to make the "Self" part of the Self Attestation possible. If there is a form for product already filled, then it will prefill all the form textFields.

https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/92062bda-6fe0-4d70-99c0-6a4dea99c681

In the image, the user is filling the Section II of the form, which requires the most inputs.

#### 3. Based on the responsibles registered for each product the trigger request is then assigned to the responsible PPSSO

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/da8d89c8-dea0-4b18-81ee-a5528023fde5)

Since the register will require step **1**, there is no interface for that yet. 
But the solution may required someone with the administrator access to edit the PRODUCT_X_RESPONSIBLE_USER table, 
which is a NxN connection between software an user, with a third field telling if the user is a ppsso of that product as well.

#### 4.The PPSSO can then trigger the "flow"
##### The flow creation is also a feature required -> The steps are constant but can be assigned to different persons -> assigned by the PPSSO

As shown above in step **2**, the PPSSO will be able to see a table of products. The same table, will also allow to start of the flow.
The next interface will shown a list with all the form sections displayed for the PPSSO

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/bdf6280e-4282-4600-bdd6-bb5d51253782)

For the section 1 and 2, cliking in `Add User` will create a list of all possible users existing in the table USERS, that are assinged for that project.
![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/00ca09aa-f8ec-4c3e-a302-0399a2f1e339)

This isn't true for section 3 though. Since it requires a signature, the only possible users that will appear are other PPSSOs.

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/e33a67e5-be33-486f-ae26-72d9d44ca710)

By selecting the required users for each section, the flow can be started. For each user assigned by each section, the system will send a notification for the user.
This can be further expanded to also notify be email, it's just a matter of adding one more function to the api.

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/4c572e18-5acc-4acd-9d1d-799131e997e0)

#### 5.Digital document signing (PDF) is a required feature

Digital documention is made using the library [pyHanko](https://github.com/MatthiasValvekens/pyHanko)

The prototype has a limited user authentication, with a table of three columns called users. Since the signature needs to be indistinguible from another, the user id is used to create the certificate and the RSA key, which is then used with pyhanko to create a certificate inside the pdf. The ppsso username can also be placed inside the key to make a more interesting signature:

![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/81392311-7b2d-4427-9447-f7441669b8ce)

The authentication is triggered after the PPSSO fills section III.

#### 6.The storage of signed PDFs should be a feature, the PDFs are encrypted with the key by PPSSO

The pdf is made using a [html template](https://github.com/JaoSchmidt/Siemens-Problem-Statement/blob/main/api/templates/engine/attestationModelRedone.html), which is then signed with the help of pyhanko, and then store inside the database a binary blob.

It can be retrieved later using the `Get Pdf` button from the `Attestations` interface:
![image](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/fb21bf69-73e4-4b02-abd6-dabe4693eecd)

#### 7. API support to trigger the flow, generation and signing of the forms from the CI/CD pipelines

Well, the API was build using flask, it supports everything that was described above.

#### 8. Import of product names from API

This is close related to step 3, since it could be said that the same administrator interface can be used to both import possible products names and assign them to their respectives PPSSOs.
