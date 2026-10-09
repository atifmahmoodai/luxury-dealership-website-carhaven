import os,re
from pathlib import Path
from urllib.parse import urlparse,unquote
from django.core.exceptions import ImproperlyConfigured
BASE_DIR=Path(__file__).resolve().parent.parent
PRODUCTION=os.getenv('ENVIRONMENT')=='production'
DEBUG=not PRODUCTION
DEMO=os.getenv('CLIENT_APPROVED')!='1'
SECRET_KEY=os.getenv('SECRET_KEY','development-only-do-not-use-on-a-live-site')
SITE_ORIGIN=os.getenv('SITE_ORIGIN','http://127.0.0.1:8000').rstrip('/')
origin=urlparse(SITE_ORIGIN)
if origin.scheme not in ('http','https') or not origin.hostname or origin.path or origin.query or origin.fragment or origin.username:raise ImproperlyConfigured('SITE_ORIGIN must be an exact HTTP(S) origin without a path')
SITE_NAME=os.getenv('SITE_NAME','CarHaven')
CONTACT_EMAIL=os.getenv('CONTACT_EMAIL','')
CONTACT_PHONE=os.getenv('CONTACT_PHONE','')
WHATSAPP=os.getenv('WHATSAPP','')
ADDRESS=os.getenv('ADDRESS','')
COMPANY_ABOUT=os.getenv('COMPANY_ABOUT','A considered approach to finding your next car. Explore the collection, take a closer look at the details, and speak to the team before arranging a visit.')
CURRENCY=os.getenv('CURRENCY','USD')
if not re.fullmatch('[A-Z]{3}',CURRENCY):raise ImproperlyConfigured('Use a three-letter CURRENCY')
if WHATSAPP and not re.fullmatch(r'[1-9][0-9]{6,14}',WHATSAPP):raise ImproperlyConfigured('WHATSAPP must be international digits without +')
if CONTACT_PHONE and not re.fullmatch(r'\+[1-9][0-9 ()-]{6,20}',CONTACT_PHONE):raise ImproperlyConfigured('Use an international CONTACT_PHONE beginning +')
if PRODUCTION and (len(SECRET_KEY)<50 or 'development-only' in SECRET_KEY or not SITE_ORIGIN.startswith('https://') or DEMO or not all([CONTACT_EMAIL,CONTACT_PHONE,ADDRESS,os.getenv('COMPANY_ABOUT')])):raise ImproperlyConfigured('Production requires a strong SECRET_KEY, HTTPS origin, CLIENT_APPROVED=1 and approved company/contact content')
ALLOWED_HOSTS=[urlparse(SITE_ORIGIN).hostname,'localhost','127.0.0.1','testserver'] if not PRODUCTION else [urlparse(SITE_ORIGIN).hostname]
CSRF_TRUSTED_ORIGINS=[SITE_ORIGIN]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','inventory']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','inventory.middleware.Protection','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='carhaven.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','inventory.context.brand']}}]
WSGI_APPLICATION='carhaven.wsgi.application'
db=os.getenv('DATABASE_URL')
if db:
 parsed=urlparse(db)
 if parsed.scheme not in ('postgres','postgresql'):raise ImproperlyConfigured('DATABASE_URL must use PostgreSQL')
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':unquote(parsed.path.lstrip('/')),'USER':unquote(parsed.username or ''),'PASSWORD':unquote(parsed.password or ''),'HOST':parsed.hostname,'PORT':parsed.port or 5432,'CONN_MAX_AGE':60}}
else:
 if PRODUCTION:raise ImproperlyConfigured('Production requires PostgreSQL DATABASE_URL')
 (BASE_DIR/'data').mkdir(exist_ok=True)
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.getenv('SQLITE_PATH',str(BASE_DIR/'data/db.sqlite3')),'OPTIONS':{'timeout':20}}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_TZ=True
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_ROOT=Path(os.getenv('MEDIA_ROOT',str(BASE_DIR/'data/photos')))
MEDIA_URL='/photos/'
FILE_UPLOAD_MAX_MEMORY_SIZE=8*1024*1024
DATA_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Strict'
SESSION_COOKIE_SECURE=PRODUCTION
CSRF_COOKIE_SECURE=PRODUCTION
SECURE_SSL_REDIRECT=PRODUCTION
SECURE_HSTS_SECONDS=31536000 if PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
# Scope HSTS to this host. Subdomain/preload enrollment is a domain-owner decision,
# not a property an application template can safely assume for an existing domain.
SILENCED_SYSTEM_CHECKS=['security.W005','security.W021']
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https') if os.getenv('TRUST_PROXY')=='1' else None
SESSION_COOKIE_AGE=28800
SECURE_REFERRER_POLICY='same-origin'
EMAIL_BACKEND='django.core.mail.backends.dummy.EmailBackend'
LOGGING={'version':1,'disable_existing_loggers':False,'handlers':{'console':{'class':'logging.StreamHandler'}},'root':{'handlers':['console'],'level':'WARNING'}}
