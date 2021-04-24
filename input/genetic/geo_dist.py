"""
API KEY for Distance Matrix

https://apis.mapmyindia.com/advancedmaps/v1/y5w387fmwteirguostpbiyrfhywxwe1v/distance_matrix/driving/12.120000,76.680000;24.879999,74.629997?rtype=0

API KEY for GEOCODING
http://api.positionstack.com/v1/forward?access_key=866f83b9c4e6b4d1daf1e9fe46d71b50&query=bhandup
"""
import socket
import requests

def geo(src,dest):
        a1="http://api.positionstack.com/v1/forward?access_key=866f83b9c4e6b4d1daf1e9fe46d71b50&query="

        res_geo1,res_geo2=requests.get(a1+src),requests.get(a1+dest)
        data_geo1,data_geo2=res_geo1.json(),res_geo2.json()
        lat1,lat2=data_geo1["data"],data_geo2["data"]
        #NEW
        lat1=lat1[0]
        lat2=lat2[0]
        '''
        src_coord=(lat1[0]['longitude'],lat1[0]['latitude'])
        dest_coord=(lat2[0]['longitude'],lat2[0]['latitude'])
        '''
        src_coord=(lat1['longitude'],lat1['latitude'])
        dest_coord=(lat2['longitude'],lat2['latitude'])
        return src_coord,dest_coord

def getDist(s,d):
	s1= "https://apis.mapmyindia.com/advancedmaps/v1/y5w387fmwteirguostpbiyrfhywxwe1v/distance_matrix/driving/"
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
def calcDist(src_name,dest_name):
	distance=getDist(src_name,dest_name)
	return distance
'''
src=input("Enter Source:")
dest=input("Enter Destination:")
print("Coordinates of source & destination: {}m".format(geo(src,dest)))
'''
