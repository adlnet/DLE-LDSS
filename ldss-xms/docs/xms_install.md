# Openlxp XMS Installation Guide

Below are the steps to install the Openlxp XMS on your local machine.


## Prerequisites

| System Requirement  | Description |
| ------------- | ------------- |
| `Python >= 3.7`| Download and install python from here [Python](https://www.python.org/downloads/).  |
| `Docker`      |  Download and install Docker from here [Docker](https://www.docker.com/products/docker-desktop).|
| `XML Security Headers` | Download and install XML Security Headers for your operating system (`libxml2-dev` and `libxmlsec1-dev` in some linux distros). |

</br>

<details>
<summary><b>Required Environment Variables</b></summary>
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

## Next Steps
 - [ECC XMS Setup & Configuration](docs/openlxp_config.md)