# #!/usr/bin/env bash
# # start-server.sh
# if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
#     (cd openlxp-xss; python manage.py createsuperuser --no-input)
# fi
# (cd openlxp-xss; gunicorn openlxp_xss_project.wsgi --reload --user python --bind 0.0.0.0:8020 --workers 2 --timeout 1200)

#!/usr/bin/env bash
# start-server.sh

# Create superuser if environment variables are provided.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    (cd openlxp-xss; python manage.py createsuperuser --no-input)
fi

# Eagerly initialize models (this forces your models to load into memory before starting Gunicorn)
echo "Eagerly initializing models..."
(cd openlxp-xss; python -c "from common.model_loader import initialize_models; initialize_models()")

# Start Gunicorn with the --preload flag.
echo "Starting Gunicorn with --preload..."
(cd openlxp-xss; gunicorn --preload openlxp_xss_project.wsgi --user python --bind 0.0.0.0:8020 --workers 2 --timeout 1200)
