## Diagrams

There are three proposals for use cases that we could come up with. But I  believe the number 2  is more aligned with the problem.

The diagrams differ in terms of automation, with bigger numbers representing increasing levels of automation.

### Use case 1
<img width="1615" alt="Use case 1" src="https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/a2573246-d07d-46b1-8b76-03f1de3f40b4">

The flask prototype doesn't have all of those use cases. Specifically, the admin and pipeline use cases. 

The pipeline represents whatever CI/CD script is used, the PPSSO and developer are common users described inside the Problem-Statment.txt, and the admin is responsible for creating and assigning the PPSSOs inside the system.

Notice that Section 3 covers the creation, signing, and storing of the PDF together. 
This is because I saw no reason to keep them separated.

### Use case 3
<img width="1615" alt="Use case 3" src="https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/3f15d6cd-6e80-45a9-a396-8bdde9f07098">

A more automated and perhaps extreme approach to the problem is  use case 3.
It would be my choice because I don't view the PPSSO and pipeline as necessarily different entities.

The development and maintenance would be entirely focused on the pipeline script and the API which could make it more stable and robust.

That assumes that manual intervention is the exception; however, that would also restrict the PPSSO and the admin to more technical levels is such cases.

### Use case 2
<img width="1615" alt="Use case 2" src="https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/4fa795f6-2baf-4ea1-944b-d62e32703058">

A more balanced approach would be to allow the full automation of pipelines and signed attestations while also creating 
an interface for the PPSSO and the admin. That would remove the technical necessity of a fully automated system, but it would be more difficult to build and maintain.

For this prototype, we chose an architecture based on this use case because it fulfills all requirements.

## Entity Relationship Diagram

The prototype has the following ER:

![ER](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/fe5474fa-639a-4729-969e-979a7b6eeca1)

This is the database we believed made the most sense. Let me dissect each table:

- **USERS**: the prototype needed some kind of authentication, so we created a pseudo user authentication with a few fake accounts to simulate the entire thing.
- **PRODUCT_X_RESPONSABLE_USER**: This is the database in which the admin would be active; it defines the relation between developers and their respective products; it also defines who is a PPSSO for the project
- **PRODUCT_X_VERSION**: This stores the all pieces of software that exist and will also link a version with its respective attestation after the flow starts.
- **ATTESTATION**: This is the attestation and its data
- **ATTESTATION_X_FORM_SECTION**: This represents every section of every attestation and also tells if some user has already filled it out.
- **FORM_SECTIONS**: This represents each form section. It can be replaced by an Enum inside the **ATTESTATION_X_FORM_SECTION**, the reason it isn't is that I didn't knew at the time.

Notice that **ATTESTATION_X_FORM_SECTION** and **FORM_SECTIONS** can be entirely removed, but this will increase the size of the attestation table.

Here is a cleaner version without those tables, it would have been my final scheme had I had more time for the prototype.

![ER2](https://github.com/JaoSchmidt/Siemens-Problem-Statement/assets/51456769/235dfb6b-05ec-4569-a0ba-b97d48401cc5)

#### Endpoints Documentation
(OBS: There are a lot of .html templates being returned, which might be weird for some API, however that is the default behavior for Flask. It is also completely optional and can be removed later to just return actual data to some separate frontend.

##### **/api/checkUser** POST
Check user credentials, and if successful, return the user ID:

*params*: <String> username, <String> pass

*return*: <Json> { 
    <String> code: “1”, “0” or “-1”,
    <String> user: USER_ID
}

##### **/api/getAttestationAlert**  POST
Get all products made by the user that still don't have an attestation yet

*params*: <String>: user_id

*return*: <String> filled template attestationAlert.html

##### **/api/components/chooseProduct**  GET
Start the interface to allow the PPSSO to initiate the flow. Opens a menu to see the products and their versions.

*return*: <Sting> filled html template with products and versions, with a jquery function to start the flow

##### **/api/checkProductsHasAttestation**  POST
Check if many products+versions already have attestations, if they do, then it also returns a list with all said products and versions.

*params*: <Array> products

*return*: <Json> { "array": hasAttestation, "code": "-1" } or { "code":"1" }

##### **/api/components/showProducts**  GET
Get all products + versions and shove them into a html template

*return*: <String> filled html template with products and versions 

##### **/api/assignUser**  POST
Get the template that allows the PPSSO to choose which section each user will fill 

*params*: <Array> products (in case of multiple trigger flows)

*return*: <String> 'OK', 'ERROR'

##### **/api/createAttestation**  POST
Effectively trigger the flow, by inserting a new empty form inside ATTESTATION 
and assinging all users inside FORM_SECTION_X_USER

*params*: <Array> products, <Array> users

*return*: <String> 'OK'

##### **/api/getUserIncompleteSections**  POST
Get all the sections of all the attestations the user needs to submit, effectivally adding a notification system.

*params*: <String> user_id

*return*: <String> filled notification template attestationAlert.html

##### **/api/getForm**  POST
Render the section form

*params*: <String> section number, <String> attestation id

*return*: <String> filled html template with all the section's inputs

##### **/api/formSubmit**  POST
Submit inputs for Section 1 into the attestation

*params*:  
     <String>: type,
     <String>: attestation,
     <String>: user_id,
     <String>: products,
     <String>: attestation_nature,
     <String>: attestation_type

*return*: <String> 'OK' or 'ERROR'

##### **/api/submitSection2**  POST
Submit inputs for Section 2 into the attestation

*params*:  
     <String>: attestation_id,
     <String>: secton_id,
     <String>: user_id,
     <String>: companyName,
     <String>: address,
     <String>: city,
     <String>: stateProvince,
     <String>: postalCode,
     <String>: country,
     <String>: website,
     <String>: name,
     <String>: title,
     <String>: contactAddress,
     <String>: phoneNumber,
     <String>: email

 *return*: 'OK' or err.msg

 
##### **/api/submitSection3**  POST
Can only be accessed after completing the 2 other sections, and only by PPSSOs
Submit inputs for Section 3 into the attestation, assuming the user decided to sign the pdfs
Then, generate a PDF using all inputs and sign the document using the PPSSO ID

*params*:  
     <String>: attestation_id,
     <String>: secton_id,
     <String>: user_id,
     <Boolean>: signature_terms,

*return* 'OK' or err.msg

##### **/api/submitSection3ThirdParty**  POST
Same as **/api/submitSection3**, but it allows the use of third party documentation (This isn't currently working in the prototype)

*params*:  
     <String>: attestation_id,
     <String>: secton_id,
     <String>: user_id,
     <Boolean>: THRID_PARTY_TERMS,
     <Binary>: THRID_PARTY_FIlE,

*return* 'OK' or err.msg
 
##### **/api/getAttestations**  POST
Get a list of all products x versions, if a there is a signed attestation, then it allows it to
download said PDF. Otherwise, show it as incomplete

*return*: filled html template with products x version and download option for signed stored PDFs
