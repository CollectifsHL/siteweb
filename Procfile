release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn marcheLibre.wsgi --log-file -
