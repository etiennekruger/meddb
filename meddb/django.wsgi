import os, site, sys

site.addsitedir('/var/www/meddb/env/lib/python2.7/site-packages')

sys.stdout = sys.stderr

path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'meddb.settings_local'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
