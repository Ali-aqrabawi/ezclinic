"""
WSGI config for simple_forms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from djangae.wsgi import DjangaeApplication



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_forms.settings")
application = DjangaeApplication(get_wsgi_application())
#application = get_wsgi_application()
