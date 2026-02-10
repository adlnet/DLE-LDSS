#!/usr/bin/env bash
# start-server.sh

cd /tmp/app/openlxp-xms/
sed -i 's/hashlib.md5()/hashlib.md5(usedforsecurity=False)/g' /tmp/app/.cache/python-packages/django/db/backends/utils.py
python manage.py waitdb 
python manage.py migrate --skip-checks
python manage.py loaddata admin_theme_data.json
python manage.py collectstatic --no-input
echo Test
cp -ur static/ /tmp/shared/
cp -ur media/ /tmp/shared/
cd /tmp/app/
pwd 
./start-server.sh