from pathlib import Path
from datetime import date
from datetime import datetime

import httpx
from webargs import fields
from starlette.routing import Route
from starlette.routing import Mount
from webargs_starlette import use_kwargs
from starlette.middleware import Middleware
from starlette.responses import FileResponse
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from webargs_starlette import WebargsHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.vedur import get_quakes
from app.logutils import get_logger

log = get_logger(__name__)


def today():
	today = date.today()
	d = datetime(
		today.year,
		today.month,
		today.day,
		23,
		59,
		59
	).isoformat()
	return d


def week_ago():
	today = date.today()
	d = datetime(
		today.year,
		today.month,
		today.day - 7
	).isoformat()
	return d


@use_kwargs(
	{
		'source': fields.String(required=False),
		'start': fields.String(required=False),
		'end': fields.String(required=False),
	},
	location='query'
)
async def quakes(request, **kwargs):
	source = kwargs.get('source', 'vedur')
	log.info(f'source: {source}')
	start = kwargs.get('start', week_ago())
	log.info(f'start: {start}')
	end = kwargs.get('end', today())
	log.info(f'end: {end}')
	if source == 'usgs':
		log.info('fetching quakes from usgs')
		rsp = httpx.get(
			'https://earthquake.usgs.gov/fdsnws/event/1/query',
			params={
				'format': 'geojson',
				'eventtype': 'earthquake',
				'minmagnitude': 1,
				'starttime': '2021-03-14T00:00:00'
			}
		).json()
	elif source == 'vedur':
		log.info('fetching quakes from vedur.is')
		rsp = get_quakes(start=start, end=end)
	else:
		log.info('fetching quakes from emsc')
		try:
			rsp = httpx.get(
				'http://www.seismicportal.eu/fdsnws/event/1/query',
				params={
					'limit': 10000,
					'start': '2021-03-07T00:00:00',
					'minlat': 61,
					'maxlat': 68,
					'minlon': -32,
					'maxlon': -4,
					'format': 'json'
				},
				timeout=15.0
			).json()
		except httpx.ReadTimeout:
			log.exception('fetching quakes from emsc timed out')
	log.info('quakes received')
	return JSONResponse(rsp)


def index(request):
	log.info('serving index.html')
	return FileResponse(html_dir.joinpath('index.html'))


async def validation_exception(request, exc):
	log.error(exc.messages)
	return JSONResponse(
		exc.messages,
		status_code=exc.status_code,
		headers=exc.headers
	)


file_path = Path(__file__).resolve()
html_dir = file_path.parents[0].joinpath('html')
log.info(f'html_dir: {html_dir}')
routes = [
	Route('/', index),
	Route('/quakes', quakes),
	Mount('/html', StaticFiles(directory=html_dir))
]
middlewares = [
	#Middleware(HTTPSRedirectMiddleware),
	Middleware(CORSMiddleware, allow_origins=['*'])
]


app = Starlette(debug=False, routes=routes, middleware=middlewares)

#app.add_middleware(HTTPSRedirectMiddleware)
#app.add_middleware(CORSMiddleware, allow_origins=['*'])
app.add_exception_handler(WebargsHTTPException, validation_exception)