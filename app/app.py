from pathlib import Path
from datetime import date
from datetime import datetime
from datetime import timedelta

import httpx
import websockets
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
	now = datetime.utcnow()
	d = now.replace(hour=23, minute=59, second=59, microsecond=0)
	return d.isoformat()


def days_ago(days=2):
	now = datetime.utcnow()
	today = now.replace(hour=0, minute=0, second=0, microsecond=0)
	days_ago = today - timedelta(days=days)
	return days_ago.isoformat()


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
	start = kwargs.get('start', days_ago())
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
				'starttime': start
			}
		).json()
	elif source == 'vedur':
		log.info('fetching quakes from vedur.is')
		rsp = get_quakes(start=start, end=end)
	elif source == 'emsc':
		log.info('fetching quakes from emsc')
		try:
			rsp = httpx.get(
				'http://www.seismicportal.eu/fdsnws/event/1/query',
				params={
					'limit': 10000,
					'start': start,
					#'minlat': kwargs.get('minlat', None), #61
					#'maxlat': kwargs.get('maxlat', None), #68
					#'minlon': kwargs.get('minlon', None), #-32
					#'maxlon': kwargs.get('maxlon', None), #-4
					'format': 'json'
				},
				timeout=15.0
			)
			rsp.raise_for_status()
			rsp = rsp.json()
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


async def hello():
	websocket_url = 'wss://www.seismicportal.eu/standing_order/websocket'
	async with websockets.connect(websocket_url) as ws:
		while True:
			msg = await ws.recv()
			print(f'received msg: {msg}')


async def health(request):
	return JSONResponse({'status': 'ok'})


async def locate(request):
	try:
		ip = request.headers.get('x-forwarded-for').split(',')[0]
		log.info(f"headers: {request.headers}")
	except Exception:
		ip = request.client.host

	#ip = '191.101.41.59'
	log.info(f"headers: {request.headers}")
	log.info(f"client_ip: {ip}")
	rsp = httpx.get(f'http://ip-api.com/json/{ip}')
	rsp.raise_for_status()
	return JSONResponse(rsp.json())


file_path = Path(__file__).resolve()
html_dir = file_path.parents[0].joinpath('html')
log.info(f'html_dir: {html_dir}')
routes = [
	Route('/', index),
	Route('/health', health),
	Route('/quakes', quakes),
	Route('/locate/', locate),
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
