import httpx
from datetime import date
from datetime import datetime

form_data = {
	"start_time": "2021-02-22 17:35:00",
	"end_time": "2021-03-01 17:35:00",
	"depth_min": 0,
	"depth_max": 25,
	"size_min": 0,
	"size_max": 7,
	"magnitude_preference": [
		"Mlw",
		"Autmag"
	],
	"event_type": ["qu"],
	"originating_system": ["SIL picks"],
	"area": [
		[68, -32],
		[61, -32],
		[61, -4],
		[68, -4]
	],
	"fields": [
		"event_id",
		"lat",
		"long",
		"time",
		"magnitude",
		"event_type",
		"originating_system"
	]
}


def default_start_time():
	today = date.today()
	d = datetime(
		today.year,
		today.month,
		today.day
	).isoformat()
	return d


def default_end_time():
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


def convert_separator_to_space(d):
	return ' '.join(d.split('T'))


def get_quakes(**kwargs):
	start = kwargs.get('start', default_start_time())
	end = kwargs.get('end', default_end_time())
	maxlon = kwargs.get('maxlon', -4)
	minlon = kwargs.get('minlon', -32)
	maxlat = kwargs.get('maxlat', 68)
	minlat = kwargs.get('minlat', 61)
	form_data = {
		"start_time": convert_separator_to_space(start),
		"end_time": convert_separator_to_space(end),
		"depth_min": kwargs.get('min_depth', 0),
		"depth_max": kwargs.get('max_depth', 25),
		"size_min": kwargs.get('min_size', 0),
		"size_max": kwargs.get('max_size', 9),
		#"magnitude_preference": ["Mlw", "Autmag"],
		#"event_type": ["qu"],
		#"originating_system": ["SIL picks"],
		"area": [
			[maxlat, minlon],
			[minlat, minlon],
			[minlat, maxlon],
			[maxlat, maxlon]
		],
		"fields": [
			"event_id",
			"lat",
			"long",
			"time",
			"magnitude",
			"depth"
			#"event_type",
			#"originating_system"
		]
	}
	rsp = httpx.post(
		'https://api.vedur.is/skjalftalisa/v1/quake/array/',
		json=form_data
	)
	rsp.raise_for_status()
	data = rsp.json()['data']
	"""
	{'data': {'event_type': ['qu', 'qu', 'qu', 'qu'],
	  'event_id': [888019, 889516, 889775, 890064],
	  'magnitude': [4.9, 4.06, 4.21, 5.07],
	  'originating_system': ['SIL picks', 'SIL picks', 'SIL picks', 'SIL picks'],
	  'long': [-22.21036, -22.21167, -22.20224, -22.14738],
	  'time': [1614562298, 1614600737, 1614607957, 1614616546],
	  'lat': [63.92493, 63.91733, 63.93121, 63.93831]}}
	"""
	#event_types = data['event_type']
	event_ids = data['event_id']
	magnitudes = data['magnitude']
	#orig_systems = data['originating_system']
	longitudes = data['long']
	times = data['time']
	latitudes = data['lat']
	depths = data['depth']
	lists = [
		event_ids,
		magnitudes,
		longitudes,
		times,
		latitudes,
		depths
	]
	ret = {}
	ret['type'] = 'FeatureCollection'
	ret['metadata'] = {}
	quakes = []
	for (event_id, magnitude, lon, time, lat, depth) in zip(*lists):
		q = {}
		q['geometry'] = {
			'type': 'Point',
			'coordinates': [lon, lat, -depth]
		}
		q['type'] = 'Feature'
		q['id'] = event_id
		q['properties'] = {
			'lon': lon,
			'lat': lat,
			'depth': depth,
			'mag': magnitude,
			#'time': time*1000
			'time': datetime.fromtimestamp(time).isoformat()
		}
		quakes.append(q)
		#quakes.append(
		#	{
		#		'event_id': event_id,
		#		'magnitude': magnitude,
		#		'longitude': lon,
		#		'time': datetime.fromtimestamp(time).isoformat(),
		#		'latitude': lat
		#	}
		#)
	ret['features'] = quakes
	return ret
