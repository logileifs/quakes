import httpx
import numpy as np
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt

today = date.today()
end_time = datetime(
	today.year,
	today.month,
	today.day,
	23,
	59,
	59
).isoformat(sep=' ')
options = {
	"start_time": "2021-02-23 00:00:00",
	"end_time": end_time,
	"depth_min": 0,
	"depth_max": 25,
	"size_min": 0,
	"size_max": 9,
	"area": [
		[64.08954074546006, -22.758045124355707],
		[63.790304623001916, -22.760791706386957],
		[63.81213105566424, -21.999988483730707],
		[63.82303793631041, -21.494617389980707],
		[63.9294607125575, -21.469898151699457],
		[64.06432591031506, -21.464404987636957]
	],
	"fields": [
		"event_id",
		"lat",
		"long",
		"time",
		"magnitude",
		"depth"
	]
}

rsp = httpx.post(
	'https://api.vedur.is/skjalftalisa/v1/quake/array/',
	json=options
)
data = rsp.json()['data']
for i, d in enumerate(data['depth'], 0):
	data['depth'][i] = -d
first_quake = datetime.utcfromtimestamp(data['time'][0]).isoformat()
last_quake = datetime.utcfromtimestamp(data['time'][-1]).isoformat()
print(f'first_quake: {first_quake}')
print(f'last_quake: {last_quake}')
fig, ax = plt.subplots(2, 2, figsize=(18, 14), sharex=False, sharey=False)
#dates = []
#for i, d in enumerate(data['time'], 0):
#	data['time'][i] = datetime.utcfromtimestamp(d).isoformat()

# frequency
days = []
for d in data['time']:
	days.append(datetime.fromtimestamp(d).timetuple().tm_yday)
days = list(set(days))
frequency = {}
for u in days:
	frequency[u] = 0
for d in data['time']:
	day = datetime.fromtimestamp(d).timetuple().tm_yday
	frequency[day] += 1
print(f'frequency: {list(frequency.values())}')
z = np.polyfit(days, list(frequency.values()), 1)
p = np.poly1d(z)
ax[0, 0].plot(days, p(days), 'r--')
ax[0, 0].plot(days, list(frequency.values()), 'k,')
ax[0, 0].set_title('Frequency', fontsize=14)

# depth
z = np.polyfit(data['time'], data['depth'], 1)
p = np.poly1d(z)
ax[1, 0].plot(data['time'], p(data['time']), 'r--')
ax[1, 0].plot(data['time'], data['depth'], 'k,')
ax[1, 0].set_title('Depth', fontsize=14)

# magnitude
z = np.polyfit(data['time'], data['magnitude'], 1)
p = np.poly1d(z)
ax[1, 1].plot(data['time'], p(data['time']), 'r--')
ax[1, 1].plot(data['time'], data['magnitude'], 'k,')
ax[1, 1].set_title('Magnitude', fontsize=14)

file = f'/home/logi/pictures/plot-{int(datetime.utcnow().timestamp())}'
fig.savefig(file)
print(f'saved as {file}')
fig.show()
input()
