import os

import dj_database_url
import environ

env = environ.Env(DEBUG=(bool, False))
site_root = environ.Path(__file__) - 2
if os.path.exists(site_root("meetenjoy", ".env")):
    environ.Env.read_env()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'zc9j11-&pu=&k*zlbo5kel6ua&=r+#oij$ao!yle1v@0o6jnyn'

DEBUG = env("DEBUG", default=False)

USE_SWAGGER = env.bool("USE_SWAGGER", default=True)
USE_SEARCH = env.bool("USE_SEARCH", default=False)
FIRST_SERVICE_URL = env.str("FIRST_SERVICE_URL", default="")
SECOND_SERVICE_URL = env.str("SECOND_SERVICE_URL", default="")
THIRD_SERVICE_URL = env.str("THIRD_SERVICE_URL", default="")
FIRST_SERVICE_RETRIES = env.int("FIRST_SERVICE_RETRIES", default=1)
SECOND_SERVICE_RETRIES = env.int("SECOND_SERVICE_RETRIES", default=1)
THIRD_SERVICE_RETRIES = env.int("THIRD_SERVICE_RETRIES", default=1)
CACHE_EXPIRES = env.int("CACHE_EXPIRES", default=60 * 5)  # seconds

ALLOWED_HOSTS = [
    "meetenjoy.herokuapp.com",
    "localhost",
    "127.0.0.1",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    "drf_yasg",
    "rest_framework_swagger",
    'allauth',
    'allauth.account',
    'django_extensions',
    'django_filters',

    'accounts',
    'aggregator',
    'meetings',
    'notifications',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meetenjoy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meetenjoy.wsgi.application'
DATABASES = {
    'default': dj_database_url.config(default=env.str("DATABASE_URL"))
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'accounts.User'

DOU_LOAD_CRONTAB = env.dict("DOU_LOAD_CRONTAB", default={"hour": 6, "minute": 1})
DOU_MEETUP_CRONTAB = env.dict("DOU_MEETUP_CRONTAB", default={"hour": 6, "minute": 1})
UPDATE_MEETING_STATUSES_CRONTAB = env.dict("UPDATE_MEETING_STATUSES_CRONTAB", default={"minute": 30})

# REDIS_HOST = env.str("REDIS_HOST", default="redis")
# REDIS_PORT = env.int("REDIS_PORT", default=6379)

# CELERY_RESULT_BACKEND = CELERY_BROKER_URL = "redis://{host}:{port}/0".format(
#     host=REDIS_HOST, port=REDIS_PORT
# )
