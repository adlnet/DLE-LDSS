#!/bin/bash
# test.sh

set -a
source .env
set +a

# Ensure the DB is up
docker-compose up -d db-xss

# Wait for MySQL to accept connections
echo "Waiting for database..."
until docker exec db mysql -u"${DB_USER}" -p"${DB_PASSWORD}" -e "SELECT 1;" &> /dev/null; do
  sleep 2
done

# Set up test DB and user permissions
docker exec db mysql -uroot -p"${DB_ROOT_PASSWORD}" <<EOSQL
CREATE DATABASE IF NOT EXISTS test_${DB_NAME}
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON ${DB_NAME}.*      TO '${DB_USER}'@'%';
GRANT ALL PRIVILEGES ON test_${DB_NAME}.* TO '${DB_USER}'@'%';
GRANT CREATE, DROP ON *.* TO '${DB_USER}'@'%';
FLUSH PRIVILEGES;
EOSQL

docker-compose --env-file .env run --entrypoint="" app sh -c "coverage run manage.py test && coverage report -m"