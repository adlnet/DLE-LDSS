# Enterprise Course Catalog: OPENLXP-XMS
This is the Experience Management Service (XMS) is the backend responsible for managing courses and catalogs and is part of the Enterprise Course Catalog OpenLXP platform.

## What is the OPENLXP-XMS?
The OPENLXP-XMS is the user interface facilitating modification and augmentation of records by learning experience owners and managers. 

This Django web application enables experience owners/managers to modify/augment experience metadata via (i.e., the "admin portal") REST API. It utilizes the Django admin UI for system configuration and management. 

## Documentation
- [Getting Started](docs/getting_started.md)
- [Openlxp XMS Installation](docs/openlxp_install.md)
- [Openlxp XMS Setup & Configuration](docs/openlxp_config.md)
- [Openlxp XMS Workflows](docs/xms_workflows.md)
- [Openlxp XMS Security](docs/openlxp_security.md)


## Prerequisites

| System Requirement  | Description |
| ------------- | ------------- |
| `Python >= 3.7`| Download and install python from here [Python](https://www.python.org/downloads/).  |
| `Docker`      |  Download and install Docker from here [Docker](https://www.docker.com/products/docker-desktop).|
| `XML Security Headers` | Download and install XML Security Headers for your operating system (`libxml2-dev` and `libxmlsec1-dev` in some linux distros). |


<details open>
<summary>Required Environment Variables</summary>
</br>

<pre><code>/.sample.env

DB_NAME= MySql database name                           
DB_USER= MySql database user
DB_PASSWORD= MySql database password
DB_ROOT_PASSWORD= MySql database root password
DB_HOST= MySql database host

DJANGO_SUPERUSER_USERNAME= Django admin user name
DJANGO_SUPERUSER_PASSWORD= Django admin user password
DJANGO_SUPERUSER_EMAIL= Django admin user email

BUCKET_NAME= S3 Bucket name where schema files are stored
AWS_ACCESS_KEY_ID= AWS access keys
AWS_SECRET_ACCESS_KEY= AWS access password
AWS_DEFAULT_REGION= AWS region

SECRET_KEY_VAL= Django Secret key to put in Settings.py

LOG_PATH= Log path were all the app logs will get stored

ENTITY_ID= The Entity ID used to identify this application to Identity Providers when using Single Sign On 
SP_PUBLIC_CERT=  The Public Key to use when this application communicates with Identity Providers to use Single Sign On
SP_PRIVATE_KEY= The Private Key to use when this application communicates with Identity Providers to use Single Sign On
CERT_VOLUME= The path to the certificate (on the host machine) to use when connecting to AWS
</code></pre>
</details>
</br>

## Installation

Expand the menu below to see the steps for installing the Openlxp XMS

<details><summary>Steps to install the ECC Openlxp XMS</summary>
</br>

1. Clone the Github repository

```bash
git clone https://github.com/OpenLXP/openlxp-xms.git"
```

2. Open terminal at the root directory of the project

```
~/PycharmProjects/openlxp-xms 
```


3. Run command to install all the requirements from requirements.txt

```
docker-compose build
```
4. Once the installation and build are done, run the below command to start the server.

```
docker-compose up
```


5. Once the server is up, go to the admin page - http://localhost:8000/admin  (replace localhost with server IP)
</details>
   

## Configuration
Expand the following drop down to see the steps for configuring the ECC Openlxp XMS.

<details><summary> Steps to Configure the Openlxp XMS </summary>


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
</details>

<details><summary>ECC XMS Troubleshooting</summary>

A good basic troubleshooting step is to use `docker-compose down` and then `docker-compose up --build` to rebuild the app image; however, this will delete everything in the database.

| Troubleshooting  | Description |
| ------------- | ------------- |
| XMLSEC | If the build fails when pip tries to install xmlsec, the issue is usually missing libraries. </br> </br> The xmlsec package includes instructions for installing the libraries on common platforms in the [documentation](https://github.com/mehcode/python-xmlsec/blob/master/README.rst#install).  |
| Line Endings      |  If the container builds but crashes or logs an error of unrecognized commands, the issue is usually incorrect line endings.</br> </br> Most IDEs/Text Editors allow changing the line endings, but the dos2unix utility can also be used to change the line endings of `start-app.sh` and `start-server.sh` to LF.|

</br>
</details>

<details><summary>Updating the ECC XMS</summary>

To update an existing installation: 

1. Pull the latest changes using git

2. Restart the application using `docker-compose restart`

</br>
</details>


<details><summary>ECC XMS Authentication</summary>

The environment variables `SP_PUBLIC_CERT`, `SP_PRIVATE_KEY` , and `SP_ENTITY_ID` must be defined (if using docker-compose the variables can be passed through).

Information on the settings for the authentication module can be found on the [OpenLXP-Authentication](docs/openlxp_auth.md).

</br>
</details>

<details><summary>ECC XMS Authorization</summary>

The setting `OPEN_ENDPOINTS` can be defined in the django settings file.

It is a list of strings (regex notation may be used) for URLs that should not check for authentication or authorization.

</br>
</details>




## Deployment 
ECC XMS is be deployed using Docker containers. Docker containers are portable, scalable, and reliable. ECC Docker images will be stored in the public Ironbanks Repo1 registry to allow anyone to pull and deploy the image. Docker images are also cloud agnostic which allows for deployment on any cloud provider. Images can be deployed as a single Docker image, a cloud provided container service, and Kubernetes for orchestration. The ECC deploys component images on Kubernetes to orchestrate containers for scalability, reliability, and high availability. 

## Testing the ECC XMS


### Component Testing 
The ECC XMS uses Pylint and Coverage for code coverage testing. To run the automated tests on the application run the command below

Test coverage information will be stored in an htmlcov directory

```bash
docker-compose --env-file .env run app sh -c "coverage run manage.py test && coverage html && flake8"
```
### End to end Testing
The ECC XMS uses cypress for system end to end testing.


