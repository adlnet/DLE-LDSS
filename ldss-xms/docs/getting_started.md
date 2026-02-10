# ECC XMS Getting Started!
The ECC contains two Client Tier services that act as the user-facing aspect of the system designed to enable human or external system/machine interactions, and consists of the following proposed components:

 - Experience Discovery Service (XDS) 

 - Experience Management Service (XMS) 

## Getting started with the ECC XMS

The Experience Management Service (XMS) is the user interface facilitating modification and augmentation of records by learning experience owners and managers. This web application enables experience owners/managers to modify/augment experience metadata (i.e., the "admin portal"). 

The XMS is a human-facing application designed to enable Experience Owners and/or Experience Managers to provide the XIS with additional/supplemental information to augment the “base” learning experience records extracted and transformed by the XIAs.


### Prerequisites

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

## Next Steps

[ECC XMS Installation Guide](docs/openlxp_install.md)