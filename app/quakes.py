import websocket


def on_message(wsapp, message):
	print('on_message')
	print(message)


wsapp = websocket.WebSocketApp(
	'wss://www.seismicportal.eu/standing_order/websocket',
	on_message=on_message
)
wsapp.run_forever()
