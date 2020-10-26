import os
from django.contrib.auth.models import User

def create_default_user():
    username = os.environ.get('MANAGEMENT_USERNAME', 'admin')
    password = os.environ.get('MANAGEMENT_PASSWORD', 'admin')
    email = os.environ.get('MANAGEMENT_EMAIL', 'admin@example.com')

    print('Trying to create default user...')

    try:
        user = User.objects.get(username=username)
        print('User already exist -> {0}'.format(user))
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password=password, email=email)
        print('User created -> {0}'.format(user))