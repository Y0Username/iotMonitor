import requests

# http://msdn.microsoft.com/en-us/library/hh441726.aspx
# get lat/lon data from http://itouchmap.com/latlong.html

# Form a rectangle and get the traffic data within the rectangle

latN = str(33.725325)
latS = str(33.58748)
lonW = str( -117.867336)
lonE = str(-117.721213)

url = 'http://dev.virtualearth.net/REST/v1/Traffic/Incidents/'+latS+','+lonW+','+latN+','+lonE

BING_KEY = 'Av6_H8GIYQyP-DLQwLOKDknW64QfmVgJmVpfiSO861v0x_j1pLPCOW6s-70nCzEW'
params = {'key': BING_KEY}


def get_severity():
	response = requests.get(url, params = params)
	data = response.json()
	resources = data['resourceSets'][0]['resources']
	print ('----------------------------------------------------')
	severitysum = 0
	for resource in resources:
	    severitysum += resource['severity']
	return severitysum


def get_traffic_data():
	data = {}
	data['severity'] = get_severity()
	return data

if __name__ == "__main__":
	response = requests.get(url, params = params)
	data = response.json()
	resources = data['resourceSets'][0]['resources']
	print ('----------------------------------------------------')
	severitysum=0;
	for resourceItem in resources:
    	 description = resourceItem['description']
    	 severity = resourceItem['severity']
    	 severitysum += severity
    	 print ('Description: ', description)
    	 print ('Severity: ', severity)
    	 print ('----------------------------------------------------')
	print ("Total traffic severity  =", severitysum)
