

# Openlxp XMS Setup & Configuration
Expand the following drop down to see the steps for configuring the ECC Openlxp XMS.


1. **On the Admin page (http://localhost:8000/admin)**
    - log in with the admin credentials that were set in the environment variables.

    </br>

2. **Configure Experience Management Service (XMS)**

    - On the django admin page click on the `Add xms configuration` button to configure the XMS and fill out the following fields.
    
    </br>

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | Target xis metadata api| Metadata API Endpoint to connect to on an XIS instance |
    | XIS catalogs api       | Catalogs API Endpoint to connect to on an XIS instance |

    </br>

3. **Configure SAML**
    - On the django admin page click on the `Add Saml configuration` button to configure the SAML and fill out the following fields.
    - **Note: Please make sure to upload schema file in the Experience Schema Server (XSS).**
    
    </br>

    | Django Admin Field  | Configuration Field Description |
    | ------------- | ------------- |
    | Name | Metadata API Endpoint to connect to on an XIS instance  |
    | Entity id     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Url     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Cert     | Catalogs API Endpoint to connect to on an XIS instance.|
    | Attribute Mapping     | Catalogs API Endpoint to connect to on an XIS instance.|

    </br>

4. **Configure XMS Email**
    - `Add sender email configuration`
        - Configure the sender email address from which conformance alerts are sent.
    - `Add receiver email configuration`
        - Add an email list to send conformance alerts. When the email gets added, an email verification email will get sent out. In addition, conformance alerts will get sent to only verified email IDs.

## Troubleshooting

A good basic troubleshooting step is to use `docker-compose down` and then `docker-compose up --build` to rebuild the app image; however, this will delete everything in the database.

| Troubleshooting  | Description |
| ------------- | ------------- |
| XMLSEC | If the build fails when pip tries to install xmlsec, the issue is usually missing libraries. </br> </br> The xmlsec package includes instructions for installing the libraries on common platforms in the [documentation](https://github.com/mehcode/python-xmlsec/blob/master/README.rst#install).  |
| Line Endings      |  If the container builds but crashes or logs an error of unrecognized commands, the issue is usually incorrect line endings.</br> </br> Most IDEs/Text Editors allow changing the line endings, but the dos2unix utility can also be used to change the line endings of `start-app.sh` and `start-server.sh` to LF.|

</br>

## Updating the Openlxp XMS

To update an existing installation: 

1. Pull the latest changes using git

2. Restart the application using `docker-compose restart`

## Deployment 
ECC XMS is be deployed using Docker containers. Docker containers are portable, scalable, and reliable. ECC Docker images will be stored in the public Ironbanks Repo1 registry to allow anyone to pull and deploy the image. Docker images are also cloud agnostic which allows for deployment on any cloud provider. Images can be deployed as a single Docker image, a cloud provided container service, and Kubernetes for orchestration. The ECC deploys component images on Kubernetes to orchestrate containers for scalability, reliability, and high availability. 

## More ECC XMS Documentation 
 - [ECC XMS Installation](docs/xms_install.md)
 - [ECC XMS Authentication](docs/openlxp_auth.md)
 - [ECC XMS Workflows](docs/xms_workflow.md)
