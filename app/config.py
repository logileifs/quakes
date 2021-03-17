from starlette.config import Config
#from starlette.datastructures import Secret

config = Config('.env')


def toupper(value):
	return str(value).upper()


DEBUG = config('DEBUG', cast=bool, default=False)
LOG_LEVEL = config('LOG_LEVEL', cast=toupper, default='INFO')
COMMIT_HASH = config('COMMIT_HASH', cast=str, default='blablabla')
VERSION = config('VERSION', cast=str, default='local-dev')
BUILD_ID = config('BUILD_ID', cast=str, default='local-dev')
#SENTRY_DSN = config(
#	'SENTRY_DSN',
#	cast=str,
#	default='https://5e107c95a2f14eb1898edcfa4cd5b622@o316263.ingest.sentry.io/5316002'
#)
#SENTRY_ENABLED = config('SENTRY_ENABLED', cast=bool, default=False)
#DB_HOST = config('DB_HOST', cast=str, default='db.logileifs.com')
#DB_PORT = config('DB_PORT', cast=str, default=28015)
#DB_USER = config('DB_USER', cast=str, default='admin')
#DB_PASSWORD = config('DB_PASSWORD', cast=Secret, default='rethinkdb')
