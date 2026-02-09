#!/usr/bin/env bash
# start-server.sh

# printenv
cd /tmp/app/openlxp-xss/

sed -i 's/hashlib.md5()/hashlib.md5(usedforsecurity=False)/g' /tmp/app/.cache/python-packages/django/db/backends/utils.py

# python manage.py waitdb 
python manage.py migrate --skip-checks
python manage.py collectstatic --no-input 
python manage.py createcachetable 
python manage.py migrate
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata admin_theme_data.json
# coverage xml
cp -ur ./static/ /tmp/shared/
cp -ur ./media/ /tmp/shared/
cd /tmp/app/ 
if [ -n "$TMP_SCHEMA_DIR" ] ; then
    (cd openlxp-xss; install -d -o python -p $TMP_SCHEMA_DIR)
else
    (cd openlxp-xss; install -d -o python -p tmp/schemas)
fi
pwd 
# service clamav-daemon restart
./start-server.sh