"""
MINIMAL WSGI CONFIGURATION
No complex imports, no potential issues
"""

import os
from django.core.wsgi import get_wsgi_application

# Set minimal environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.absolute_minimal_settings')

# Get WSGI application
application = get_wsgi_application()
