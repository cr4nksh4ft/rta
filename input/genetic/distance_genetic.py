#Mumbai-Pune
#lat,long
#(19.131577,72.891418) (18.519479,73.870703)
import socket
import requests
#import yaml
import pickle
import json
import flexpolyline as fp

from .geo_dist import geo

#import weather
import json
import random
from operator import itemgetter
#src='https://router.hereapi.com/v8/routes?transportMode=car&origin=19.131577,72.891418&destination=18.519479,73.870703&alternatives=6&return=polyline,summary&apiKey=t0a0rc7zIq7H_R53AXFFs0B3L4QNsMTa9p_TW7MrKnk'
def getUserInput():
    '''
    ACCEPT WAYPOINTS FROM USER
    THE MORE THE MERRIER.
    RETURNS SEGMENTS
    EXAMPLE - waypoints = Mumbai, Pune, Delhi
    Then segments = ('Mumbai','Pune'), ('Pune','Delhi')
    '''
    waypoints=[]
    #ENTER MINIMUM 5 POINTS IN TOTAL
    #FOR TESTING YOU MAY ENTER JUST TWO
    while(True):
        waypoint=input("Enter city name | q to quit: ")
        if (waypoint == "q"):
            break
        waypoints.append(waypoint)
    #CREATE AND POPULATE THE LIST
    segments=[(waypoints[i],waypoints[i+1]) for i in range(len(waypoints)-1)]
    print("SEGMENTS",segments,sep="=>")
    #RETURN LIST OF FORMED SEGMENTS
    return segments

def getAllData(segments):
    '''
    INPUT > segments = [('A','B'),('B','C')..]

    COLLECTS all data from Here Routing api v8
    Segment Routes have flexpolyline encoding. Decode them for coordinates

    STORES DATA INTO FILE. SEE data.txt
    Filter data as per requirement

    OUTPUT > NONE.
    '''
    #A dict which stores data about segments
    #A segment is a route between two points
    segmentData={}
    for segment in segments:
        coord=None

        while (coord==None):
            try:
                coord=geo(*segment)
            except:
                pass

        w1coord=str(coord[0][0])+","+str(coord[0][1])
        w2coord=str(coord[1][0])+","+str(coord[1][1])
        src="https://router.hereapi.com/v8/routes?transportMode=car&origin={}&destination={}&alternatives=6&return=polyline,travelSummary&apiKey=t0a0rc7zIq7H_R53AXFFs0B3L4QNsMTa9p_TW7MrKnk".format(w1coord,w2coord)
        data=requests.get(src)
        data=data.json()
        print("data",data)
        segmentData[segment]=data
    #Serialize & store segmentData dict in file using pickle
    datafile=open('data.txt','wb')
    pickle.dump(segmentData,datafile)
    datafile.close()
    '''
    datafile=open('data.txt','w')
    yaml.dump(segmentData,datafile)
    datafile.close()
    '''
    return

#Filter specific data from all data.
def getDataFromFile():
    '''
    segment_pool -A DICT THAT STORES ALL SEGMENT POLYLINES AND EVALUATION PARAMETERS I.E DISTANCE OR ACCIDENT SCORE AGAINST THEIR SEGMENT NAMES"

    EVERY ENTRY STORES data about AVAILABLE ROUTES BETWEEN TWO POINTS.
    LET'S CALL THEM ROUTE TUPLES
    Example:
    segment_pool={
        "('A','B')" : [
            (0, polyline, dist, accidentScore),
            (1, polyline, dist, accidentScore)
            .
            .
            ]
        .
        .
        .
    }
    OUTPUT DICT segment_pool
    '''
    segment_pool={}
    #open the data file in binary read mode 'rb'
    datafile = open("data.txt", 'rb')
    datafile = pickle.load(datafile)
    '''
    datafile = open("data.txt", 'r')
    datafile = yaml.load(datafile,Loader=yaml.FullLoader)
    '''
    #FEED THE segment_pool
    for key in datafile.keys():
        #Key's value is initially an empty list
        segment_pool[key]=[]
        #Feed the empty list with all possible route tuples
        for idx,route in enumerate(datafile[key]['routes']):
            polyline=route['sections'][0]['polyline']
            duration=route['sections'][0]['travelSummary']['duration']
            distance=route['sections'][0]['travelSummary']['length']
            '''
                ADD ATTRIBUTE WEATHER, ACCIDENT_RECORD, elevation
                weather ke liye call karna padega
                coord file se milega
                steepness vagera IOT se lena padega? FAR THOUGHT
            '''
            #LAT, LONG
            sourceL=route['sections'][0]['departure']['place']['location']
            destL=route['sections'][0]['arrival']['place']['location']
            s_coord=(sourceL['lat'],sourceL['lng'])
            d_coord=(destL['lat'],destL['lng'])
            #weather,traction,accidentHistory = getCriticalData(s_coord,d_coord)
            #accidentScore = getCriticalData(s_coord,d_coord)
            segment_pool[key].append((idx,polyline,duration,distance))
            print("\n")
    return segment_pool

def getCriticalData(s_coord,d_coord):
    '''
    accidentHistory = random.randrange(0,10)
    traction = random.randrange(0,10)
    weather = random.randrange(0,10)
    '''
    return random.randrange(0,10)

#GENETIC ALGO. FUNCTIONS
def generatePopulation(pool,loop=None,population=None):
    population=[]
    for _ in range(loop):
        chromosome=[]
        '''
        iterate over items in dictionary and select one randomly from each
        '''
        for segment in pool:
            chromosome.append(random.choice(pool[segment]))
        population.append(chromosome)
    #print(*population,sep="\nNew Chromosome\n")
    return population

def calcFitness(population,flag=False):
    '''
    calculate fitness of each chromosome in Population
    if flag=True, dont append accident value, update it.
    Implemented below
    '''
    for chromosome in population:
        if(flag):
            end=len(chromosome)-1
        else:
            end=len(chromosome)
        total_dist=0
        for gene in chromosome[0:end]:
            total_dist+=gene[-1]
        if(flag):
            chromosome[-1]=total_dist
        else:
            chromosome.append(total_dist)
    return population

def selectFittest(population, percent=50):

    population = sorted(population,key=itemgetter(-1))
    select = int((percent/100)*(len(population)))
    return population[0:select+1]

def crossover(fittest_routes,loop=10):
    '''
    return new generation after mixing
    '''
    for _ in range(loop):
        parents = random.choices(fittest_routes,k=2)
        #parents = random.sample(fittest_routes,k=2)
        crossover_point = random.randrange(0,len(parents[0])-1)
        for i in range(crossover_point):
            parents[0][i],parents[1][i] = parents[1][i],parents[0][i]
        fittest_routes.extend(parents)
    return fittest_routes

'''
PERFORM MUTATION TO PREVENT PREMATURE CONVERGENCE
?????????????????????????????????????????????????
'''
def getFinalRoutes(waypoint,gen_count=10):
    '''
    INPUT > segment_list = [('A','B'),('B','C')...]
            gen_count = no. of generations required. Default=10
    OUTPUT > latest generation of routes
             format [ [(),(),..,score], [(),(),..,score], [(),(),..,score] ] (Sorted)
    '''
    segs =[(waypoint[i],waypoint[i+1]) for i in range(len(waypoint)-1)]
    getAllData(segs)
    data = getDataFromFile()
    population=[]
    flag=False
    #PRODUCE GENERATIONS
    for i in range(gen_count):
        if(i==0):
            population = generatePopulation(data,loop=10)
        popu_with_fitness = calcFitness(population,flag)
        fittest_routes = selectFittest(popu_with_fitness)
        population=crossover(fittest_routes)
        flag=True
    return sorted(population,key = itemgetter(-1))

def main():
    segs=getUserInput()
    getAllData(segs)
    pool=getDataFromFile()
    population=[]
    flag=False
    #PRODUCE 10 GENERATIONS
    for i in range(10):
        if(i==0):
            population = generatePopulation(pool,loop=10)
        popu_with_fitness = calcFitness(population,flag)
        fittest_routes = selectFittest(popu_with_fitness)
        population=crossover(fittest_routes)
        flag=True
    solution_file=open('solution.txt','wb')
    pickle.dump(population,solution_file)
    solution_file.close()

def getAllCoordinates(waypoint,gen_count=10):
    '''
    INPUT > Waypoints = ['A',B','C']
            gen_count = no. of generations required. Default=10
    OUTPUT > [
                (50.10228, 8.69821),
                (50.10201, 8.69567),
                (50.10063, 8.69150),
                .
                .
                .
             ]
    '''
    segmentList =[(waypoint[i],waypoint[i+1]) for i in range(len(waypoint)-1)]

    getAllData(segmentList)

    data = getDataFromFile()
    population=[]
    all_coordinates=[]
    flag=False
    #PRODUCE GENERATIONS
    for i in range(gen_count):
        if(i==0):
            population = generatePopulation(data,loop=10)
        popu_with_fitness = calcFitness(population,flag)
        fittest_routes = selectFittest(popu_with_fitness)
        population=crossover(fittest_routes)
        flag=True
    population=sorted(population,key = itemgetter(-1))
    route=population[0]
    for segment in route[0:-1]:
        polyline=segment[1]
        all_coordinates.extend(fp.decode(polyline))
    return all_coordinates
