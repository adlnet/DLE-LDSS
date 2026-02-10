# OpenLXP-Authentication

This is a Django package built on the social-auth-app-django package to allow additional authentication options for the OpenLXP project.

Currently this package adds support for storing SAML configurations in the database used by Django, to allow for site administrators to set SAML configurations through the admin app.

</br>

## Setup

To install this package install the dependencies from the requirements file (this should happen automatically if using pip) (make sure libxml2-dev libxmlsec1-dev are installed if running in Docker).

<details open ><summary>Steps for Openlxp-Auth Setup </summary>

1. Add the required settings to the Django settings file, social_django settings may also be used.

2. Add the included URLs to Django (this will add the social_django URLs for you).

```python
urlpatterns = [
    ...
    url('', include('openlxp_authentication.urls')),
]
```

3. Access the `/saml/metadata/` endpoint to view the configuration XML and verify it is correct (if AssertionConsumerService Location is incorrect, there are optional settings to fix it).

4. Upload the XML to needed IDPs.

5. Login to the admin module to add IDP configurations (the name setting will be used to identify which configuration to use).
</details>


</br>

## To test the login configuration: 
<details open ><summary>Steps for Testing the Openlxp-Auth</summary>

1. Logout if you are already logged in

2. Access `/login/samldb/?idp=nameFromConfig`

3. You should be redirected to your chosen IDP

4. Login with your IDP

5. You will be returned to the application and sent to the REDIRECT_URL if set
</details>

## Settings 
Expand the following dropdowns to see the Required and Optional Settings


<details open><summary><b>Required Settings</b></summary>

</br> These settings are REQUIRED for the setup & configuration of the Openlxp-Auth</br>

| Setting Name  | Example | Description |
| ------------- | ------------- |  ------------- |
| JSONFIELD_ENABLED | `JSONFIELD_ENABLED = True`| Allows storing the attribute mapping as JSON in the database. |
| USER_MODEL | `USER_MODEL = 'core.XDSUser'` | Sets what model should be used when authenticating a User |
| SP_ENTITY_ID | `SP_ENTITY_ID = 'http://localhost:8000'` | Sets Entity ID that IDPs should use for identifying the service.  <b><i>This setting should be unique to your service</i></b> |
| SP_PUBLIC_CERT | `SP_PUBLIC_CERT = "******"` |  Sets the public key to be used when authenticating users |
| SP_PRIVATE_KEY | `SP_PRIVATE_KEY = "******"` |  Sets the private key to be used when authenticating users |
| CONTACT INFO | ORG_INFO = { </br>"en-US": { </br>"name": "example", </br>"displayname": "Example Inc.", </br>"url": "http://localhost", </br> } </br> TECHNICAL_CONTACT = {</br> "givenName": "Tech Gal", </br> "emailAddress": "technical@localhost.com" </br> } </br> SUPPORT_CONTACT = { </br> "givenName": "Support Guy", </br> "emailAddress": "support@localhost.com", </br> } </br> } </br>  |  Set in three settings to provide to IDPs; </br> - ORG_INFO, </br> - TECHNICAL_CONTACT, </br> - SUPPORT_CONTACT. |
| USER_ATTRIBUTES | USER_ATTRIBUTES = [ </br>"user_permanent_id", </br>"first_name", </br>"last_name", </br>"email" </br>]  |  list the attributes of the User model that should be retreived from the IDP. </br> </br>This setting is used to set the default value for the attribute map in the IDP configuration |
| AUTHENTICATION_BACKENDS | AUTHENTICATION_BACKENDS = ( </br> ...  </br>     'django.contrib.auth.backends.ModelBackend',  </br>     'openlxp_authentication.models.SAMLDBAuth',</br>) |  MUST INCLUDE `'openlxp_authentication.models.SAMLDBAuth'`, but others can included as desired. |
| INSTALLED_APPS | INSTALLED_APPS = [ </br> ... </br> 'social_django', </br> 'openlxp_authentication', </br>] |  Sets what apps Django should load. </br> </br> Both social_django and openlxp_authentication must be added for this package to work correctly. |
</details>

</br>


<details><summary><b>Optional Settings</b></summary>

</br>These settings are optional for the setup & configuration of the Openlxp-Auth</br> 

| Setting Name  | Example | Description |
| ------------- | ------------- |  ------------- |
| SESSION_EXPIRATION | `SESSION_EXPIRATION = True`| Has the Django session expiration match an expiration supplied by the IDP. |
| LOGIN_REDIRECT_URL | `LOGIN_REDIRECT_URL = 'http://www.google.com'` | used by the application to redirect the user upon  successful login. |
| OVERIDE_HOST | `OVERIDE_HOST = 'http://localhost:8000'` | The OVERIDE_HOST setting is used when Django is not able to accurately determine the host and port being used (this can occur in certain reverse proxy configurations). </br> </br> The setting must follow the format `http://www.hostname.com:port`, `https://` may be used instead.</br> </br>If this setting is supplied, SOCIAL_AUTH_STRATEGY and BAD_HOST should also be set.|
| BAD_HOST< | `BAD_HOST = 'http://localhost'` |  The BAD_HOST setting is used to remove part of the host and port string if the automatically detected configuration is incorrect. </br> </br> Similar to OVERIDE_HOST, this setting should also start with either `http://` or `https://`. </br> </br> The setting is required if using the OVERIDE_HOST setting. |
| SOCIAL_AUTH_STRATEGY | `SOCIAL_AUTH_STRATEGY = 'openlxp_authentication.models.SAMLDBStrategy'` |  The SOCIAL_AUTH_STRATEGY setting is required if using the OVERIDE_HOST setting.  OpenLXP-Authentication provides a strategy but custom solutions can be created and referenced in this setting. |

</details>
</br>

## EXAMPLE SETTINGS.PY

<details><summary>EXAMPLE SETTINGS.PY</summary>

```ini
/Settings.py
# ************************ REQUIRED SETTINGS ************************

# **JSONFIELD_ENABLED** 
# : The JSONFIELD_ENABLED setting is required as it allows storing the attribute mapping as JSON
# : in the database.
JSONFIELD_ENABLED = True

# USER_MODEL 
# : The USER_MODEL setting sets what model should be used when authenticating a User.
USER_MODEL = 'core.XDSUser'

# SP_ENTITY_ID
# : The SP_ENTITY_ID setting sets Entity ID that IDPs should use for identifying the service.  
# : This settings should be unique to your service.
SP_ENTITY_ID = 'http://localhost:8000'

# SP_PUBLIC_CERT
# : The SP_PUBLIC_CERT setting sets the public key to be used when authenticating users.
SP_PUBLIC_CERT = "******"

# SP_PUBLIC_KEY
# : The SP_PRIVATE_KEY setting sets the private key to be used when authenticating users.
SP_PRIVATE_KEY = "******"

# Contact Info
# : Contact information is set in three settings to provide to IDPs; 
# : ORG_INFO, TECHNICAL_CONTACT, and SUPPORT_CONTACT.
ORG_INFO = {
    "en-US": {
        "name": "example",
        "displayname": "Example Inc.",
        "url": "http://localhost",
    }
}
TECHNICAL_CONTACT = {
    "givenName": "Tech Gal",
    "emailAddress": "technical@localhost.com"
}
SUPPORT_CONTACT = {
    "givenName": "Support Guy",
    "emailAddress": "support@localhost.com",
}

# USER_ATTRIBUTES
# : The USER_ATTRIBUTES setting list the attributes of the User model that should be retrieved from the IDP.
# : This setting is used to set the default value for the attribute map in the IDP configuration
USER_ATTRIBUTES = ["user_permanent_id",
        "first_name",
        "last_name",
        "email"]


# AUTHENTICATION_BACKENDS
# : The AUTHENTICATION_BACKENDS setting sets what authentication services should be avaliable.
# : This setting must include `'openlxp_authentication.models.SAMLDBAuth'`, but others can included as desired.
AUTHENTICATION_BACKENDS = (
    ...
    'django.contrib.auth.backends.ModelBackend',
    'openlxp_authentication.models.SAMLDBAuth',
)

# INSTALLED_APPS
# : The INSTALLED_APPS setting sets what apps Django should load.
# : Both social_django and openlxp_authentication must be added for this package to work correctly.
INSTALLED_APPS = [
    ...
    'social_django',
    'openlxp_authentication',
]

# ************************ OPTIONAL SETTINGS ************************

# SESSION_EXPIRATION
# : The SESSION_EXPIRATION setting has the Django session expiration match an experiation supplied by the IDP.
SESSION_EXPIRATION = True

# LOGIN_REDIRECT_URL
# : The LOGIN_REDIRECT_URL setting is used by the application to redirect the user upon successful login.
LOGIN_REDIRECT_URL = 'http://www.google.com'

# OVERIDE_HOST
# : The OVERIDE_HOST setting is used when Django is not able to accurately determine the host 
#   and port being used (this can occur in certain reverse proxy configurations).  
# : The setting must follow the format `http://www.hostname.com:port`, `https://` may be used instead.
# : If this setting is supplied, SOCIAL_AUTH_STRATEGY and BAD_HOST should also be set.
OVERIDE_HOST = 'http://localhost:8000'

# BAD_HOST
# : The BAD_HOST setting is used to remove part of the host and port string if the automatically
#   detected configuration is incorrect.
# : Similar to OVERIDE_HOST, this setting should also start with either `http://` or `https://`.
# : The setting is required if using the OVERIDE_HOST setting.
BAD_HOST = 'http://localhost'

# SOCIAL_AUTH_STRATEGY

# : The SOCIAL_AUTH_STRATEGY setting is required if using the OVERIDE_HOST setting. 
# :  OpenLXP-Authentication provides a strategy but custom solutions can be created and referenced in this setting.
SOCIAL_AUTH_STRATEGY = 'openlxp_authentication.models.SAMLDBStrategy'

```
</details>

## More ECC XMS Documentation
 - 


