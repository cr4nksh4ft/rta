"""
API KEY for Distance Matrix

https://apis.mapmyindia.com/advancedmaps/v1/apikey/distance_matrix/driving/12.120000,76.680000;24.879999,74.629997?rtype=0


"""
import socket
import requests

def waypointGeo(waypoints):
	coord_dict = {}
	a1="https://geocode.search.hereapi.com/v1/geocode?q="
	a3="&apiKey=apikey"
	for waypoint in waypoints:
		res_geo = requests.get(a1+waypoint+a3)
		data_geo = res_geo.json()
		pos = data_geo['items'][0]['position']
		coord_dict[waypoint] = (str(pos['lat']),str(pos['lng']))
	return coord_dict

def geo(src,dest):
	a1="https://geocode.search.hereapi.com/v1/geocode?q="
	a3="&apiKey=apikey"
	res_geo1,res_geo2=requests.get(a1+src+a3),requests.get(a1+dest+a3)


	data_geo1,data_geo2=res_geo1.json(),res_geo2.json()

	lat1,lat2=data_geo1['items'][0]['position'],data_geo2['items'][0]['position']

        #NEW
	'''
        lat1=lat1[0]
        lat2=lat2[0]

	src_coord=(lat1['longitude'],lat1['latitude'])
        dest_coord=(lat2['longitude'],lat2['latitude'])
        '''

	src_coord=(lat1['lat'],lat1['lng'])

	dest_coord=(lat2['lat'],lat2['lng'])
	return src_coord,dest_coord

def latlong (src):
	a1="https://geocode.search.hereapi.com/v1/geocode?q="
	a3="&apiKey=apikey"
	res_geo1=requests.get(a1+src+a3)
	data_geo1=res_geo1.json()
	lat1=data_geo1['items'][0]['position']
	src_coord=[lat1['lat'],lat1['lng']]
	return src_coord

def getDist(s,d):

	s1= "https://apis.mapmyindia.com/advancedmaps/v1/apikey/distance_matrix/driving/"
	s_coord,d_coord = geo(s,d)
	#api_address =s1+str(s_coord[0])+','+str(s_coord[1])+';'+str(d_coord[0])+','+str(d_coord[1])+'?rtype=1&region=ind'
	api_address=s1+"{},{};{},{}?rtype=1&region=ind".format(str(s_coord[0]),str(s_coord[1]),str(d_coord[0]),str(d_coord[1]))
	res = requests.get(api_address)
	data = res.json()
	result = data["results"]["distances"]
	dist = result[0][1]

	return dist

#Import this file
#Call this function in your py file
def weather(city):
    try:
        a1="http://api.openweathermap.org/data/2.5/weather?units=metric"
        a2 = "&q=" + city
        a3 = "&appid=apikey"
        api_address =  a1 + a2  + a3
        res = requests.get(api_address)
        #print(res)
        data=res.json()
        #print(data)
        temp=data['main']['temp']
        a="\n Temperature: "+str(temp)
        pressure=data['main']['pressure']
        a="\nPressure: "+str(pressure)
        visibility = data['visibility']
        b="\nVisibility: "+str(visibility)
        wind = data['wind']['speed']
        c="\n Wind Speed : "+str(wind)
        weather = data['weather']
        weather_main = weather[0]
        d="\n Weather Description: "+str(weather_main['description'])
        final=a+b+c+d
        return (final)
    except OSError as e:
        return (e)
    except KeyError as e1:
        print("Check city name ",e1)

def calcDist(src_name,dest_name):
	distance=getDist(src_name,dest_name)
	return distance

'''
src=input("Enter Source:")
dest=input("Enter Destination:")
print("Coordinates of source & destination: {}m".format(geo(src,dest)))
'''
