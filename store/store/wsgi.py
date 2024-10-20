"""
WSGI config for store project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/home/ubuntu/myproject')
sys.path.append('/home/ubuntu/myproject/venv/lib/python3.12/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
