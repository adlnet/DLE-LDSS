# OpenLXP XMS Application Security
## Overview
This README provides an overview of security-related configurations for the OpenLXP XMS application.

### Openlxp Security Features
| Security Feature  | Example | Description |
| ------------- | ------------- |  ------------- |
| Django Secret Key | `SECRET_KEY = os.environ.get('SECRET_KEY_VAL')`| The SECRET_KEY setting is a secret unique to your particular Django installation. It is used in various places to provide a source of cryptographically secure pseudo-randomness. You must keep this value secret. A leakage of this value could lead to various attacks. </br> </br> The secret key is fetched from an environment variable SECRET_KEY_VAL. You should set this environment variable in your production environment and ensure it is not checked into version control systems. |
| Debug Mode | `DEBUG = False` | Ensure that DEBUG is set to False in your production environment to prevent sensitive data from being displayed in error messages. |
| Allowed Hosts | `ALLOWED_HOSTS = os.environ.get('HOSTS').split(';')'` | Set the ALLOWED_HOSTS to the hostname or IP address of your server. For multiple hosts, separate them with a semicolon (;) |
| Content Security Policy (CSP) | `SP_PUBLIC_CERT = "******"` |  The Content Security Policy (CSP) helps prevent a wide range of attacks, including Cross-site scripting (XSS) and other code-injection attacks. In your settings.py file, you'll find CSP configurations such as CSP_DEFAULT_SRC and CSP_SCRIPT_SRC. </br> </br> The source for each content type is currently set to 'self', meaning it only allows resources from the same origin. Adjust these settings to suit your specific needs.|
| CSRF and Session Cookie | `CSRF_COOKIE_SECURE = True` </br> `SESSION_COOKIE_SECURE = True`|  CSRF_COOKIE_SECURE and SESSION_COOKIE_SECURE settings ensure that the CSRF and session cookies will only be sent over HTTPS. This is essential in a production environment to prevent session ID theft. |
| CORS Configuration | `CORS_ALLOWED_ORIGINS = [os.environ.get('CORS_ALLOWED_ORIGINS')]`<br/>`CORS_ALLOW_CREDENTIALS = True` <br/>`CSRF_COOKIE_DOMAIN = os.environ.get('CSRF_COOKIE_DOMAIN')` </br>`CSRF_TRUSTED_ORIGINS = [os.environ.get('CSRF_COOKIE_DOMAIN'), ]`|  Set CORS_ALLOWED_ORIGINS to the domains allowed to access your API. CORS_ALLOW_CREDENTIALS should be True to allow cookies to be included in cross-origin HTTP requests. |
| Password Validation | ------------- |  Django enforces strong passwords with its set of password validators, configured in AUTH_PASSWORD_VALIDATORS in the Settings.py. |
| Secure SSL Redirect | ------------- |  If TESTING is not set to 'true', all non-HTTPS requests are redirected to HTTPS, thanks to SECURE_SSL_REDIRECT. |
| Database Configuration | ------------- |  Configure your database settings under DATABASES in your environment variables.|
| Authentication | AUTHENTICATION_BACKENDS = (</br>'django.contrib.auth.backends.ModelBackend',</br>'rest'</br>) |  The authentication backends are set to Django's ModelBackend and the REST framework's TokenAuthentication method. |


## More ECC XMS Documentation
 - [ECC XMS Installation](docs/xms_install.md)
 - [ECC XMS Authentication](docs/openlxp_auth.md)
 - [ECC XMS Workflows](docs/xms_workflow.md)