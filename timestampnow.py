import datetime

def get_time():
	current_date_time = datetime.datetime.now()
	date_time = {}
	date_time["id"]= str(currentdatetime)
	date_time["month"]= currentdatetime.month
	date_time["weekday"]= currentdatetime.weekday()
	date_time["hour"]= currentdatetime.hour
	date_time["minute"]= currentdatetime.minute
	date_time['day'] = currentdatetime.day
	return date_time;
