import datetime

def get_time():
	time_now = datetime.datetime.now()
	date_time = {}
	date_time["id"]= str(time_now)
	date_time["month"]= time_now.month
	date_time["weekday"]= time_now.weekday()
	date_time["hour"]= time_now.hour
	date_time["minute"]= time_now.minute
	date_time['day'] = time_now.day
	return date_time;
