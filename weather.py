import pyowm

API_key = '20cd84de3f7b25758bc01d7c28595267'
owm = pyowm.OWM(API_key)
latlong = (33.643431, -117.841121)

def get_weather_data():
	weather = {}
	obs = owm.weather_at_coords(*latlong)
	w = obs.get_weather()
	weather['temperature'] = w.get_temperature(unit='celsius')
	weather['humidity'] = w.get_humidity()
	weather['w_description'] = "Partly Cloudy"
	return weather
