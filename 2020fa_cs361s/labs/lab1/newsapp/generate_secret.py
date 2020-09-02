from django.core.management.utils import get_random_secret_key

with open("django_secret_key.txt", "w+") as f:
    f.write(get_random_secret_key())
