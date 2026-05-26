#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); username = os.environ.get('DJANGO_SUPERUSER_USERNAME'); email = os.environ.get('DJANGO_SUPERUSER_EMAIL', ''); password = os.environ.get('DJANGO_SUPERUSER_PASSWORD'); assert username and password, 'Faltan variables del superusuario'; user, created = User.objects.get_or_create(username=username, defaults={'email': email}); user.email = email or user.email; user.is_staff = True; user.is_superuser = True; user.set_password(password); user.save(); print('Superusuario configurado correctamente:', username)"
