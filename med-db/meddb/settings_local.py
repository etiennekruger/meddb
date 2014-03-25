from settings import *

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.join(PROJECT_ROOT, '..'), "med-db.db"),
    }
}
