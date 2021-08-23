# TODO Add the right values
from tempfile import mkdtemp
from decouple import config

DOMAIN = config('DOMAIN', default='0.0.0.0')
PORT = config('PORT', default='5000')
tool_config = {
    "DEBUG": config('DEBUG', default=True, cast=bool),
    "ENV": "production",
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 600,
    "SECRET_KEY": "EF186261-4F2E-4CCC-9C5C-6935CF0262F4",
    "SESSION_TYPE": "filesystem",
    "SESSION_FILE_DIR": mkdtemp(),
    "SESSION_COOKIE_NAME": "flask-session-id",
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SECURE": True,  # should be True in case of HTTPS usage (production)
    "SESSION_COOKIE_SAMESITE": "None",  # should be 'None' in case of HTTPS usage (production)
    "DEBUG_TB_INTERCEPT_REDIRECTS": False,
    "SERVER_NAME": DOMAIN + (':' + PORT) if PORT != '80' else '',
    "LEARN_REST_KEY" : "somekey",
    "LEARN_REST_SECRET" : "somekey",
    "LEARN_REST_HOST" : "somekey",
    "APP_URL" : "somekey",
    "VERIFY_CERTS" : 'True'
}