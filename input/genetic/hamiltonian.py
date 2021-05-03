import pandas as pd
import numpy as np
import random
from itertools import combinations
from .geo_dist import waypointGeo
import requests
import flexpolyline as fp

#import sys

def gatherData(waypoints):
    all_waypoints = waypoints
    waypoint_distances = {}
    waypoint_durations = {}
    coord_dict = waypointGeo(all_waypoints)
    polyline_dict = {}
    for (waypoint1, waypoint2) in combinations(all_waypoints, 2):
        try:
            lat_lng_1=coord_dict[waypoint1][0]+","+coord_dict[waypoint1][1]
            lat_lng_2=coord_dict[waypoint2][0]+","+coord_dict[waypoint2][1]
            src = "https://router.hereapi.com/v8/routes?transportMode=car&origin={}&destination={}&routingMode=short&return=polyline,travelSummary&apiKey=t0a0rc7zIq7H_R53AXFFs0B3L4QNsMTa9p_TW7MrKnk".format(lat_lng_1, lat_lng_2)
            route = requests.get(src)
            route = route.json()

            distance = route['routes'][0]['sections'][0]['travelSummary']['length']

            duration = route['routes'][0]['sections'][0]['travelSummary']['duration']

            polyline = route['routes'][0]['sections'][0]['polyline']

            waypoint_distances[frozenset([waypoint1, waypoint2])] = distance
            waypoint_durations[frozenset([waypoint1, waypoint2])] = duration
            polyline_dict[frozenset([waypoint1, waypoint2])] = polyline

        except Exception as e:
            print(e)
            print("Error with finding the route between %s and %s." % (waypoint1, waypoint2))

    with open("my-waypoints-dist-dur.tsv", "w") as out_file:
        out_file.write("\t".join(["waypoint1",
                                  "waypoint2",
                                  "distance_m",
                                  "duration_s"]))

        for (waypoint1, waypoint2) in waypoint_distances.keys():
            out_file.write("\n" +
                           "\t".join([waypoint1,
                                      waypoint2,
                                      str(waypoint_distances[frozenset([waypoint1, waypoint2])]),
                                      str(waypoint_durations[frozenset([waypoint1, waypoint2])])]))
    return polyline_dict

def readData():
    waypoint_distances = {}
    waypoint_durations = {}
    all_waypoints = set()

    waypoint_data = pd.read_csv("my-waypoints-dist-dur.tsv", sep="\t")

    for i, row in waypoint_data.iterrows():
        waypoint_distances[frozenset([row.waypoint1, row.waypoint2])] = row.distance_m
        waypoint_durations[frozenset([row.waypoint1, row.waypoint2])] = row.duration_s
        all_waypoints.update([row.waypoint1, row.waypoint2])
    return all_waypoints,waypoint_distances,waypoint_durations


def compute_fitness(solution, waypoint_distances):
    """
        This function returns the total distance traveled on the current road trip.

        The genetic algorithm will favor road trips that have shorter
        total distances traveled.
    """

    solution_fitness = 0.0

    for index in range(len(solution)):
        waypoint1 = solution[index - 1]
        waypoint2 = solution[index]
        solution_fitness += waypoint_distances[frozenset([waypoint1, waypoint2])]

    return solution_fitness

def generate_random_agent(all_waypoints):
    """
        Creates a random road trip from the waypoints.
    """

    new_random_agent = list(all_waypoints)
    random.shuffle(new_random_agent)
    return tuple(new_random_agent)

def mutate_agent(agent_genome, max_mutations=3):
    """
        Applies 1 - `max_mutations` point mutations to the given road trip.

        A point mutation swaps the order of two waypoints in the road trip.
    """

    agent_genome = list(agent_genome)
    num_mutations = random.randint(1, max_mutations)

    for mutation in range(num_mutations):
        swap_index1 = random.randint(0, len(agent_genome) - 1)
        swap_index2 = swap_index1

        while swap_index1 == swap_index2:
            swap_index2 = random.randint(0, len(agent_genome) - 1)

        agent_genome[swap_index1], agent_genome[swap_index2] = agent_genome[swap_index2], agent_genome[swap_index1]

    return tuple(agent_genome)

def shuffle_mutation(agent_genome):
    """
        Applies a single shuffle mutation to the given road trip.

        A shuffle mutation takes a random sub-section of the road trip
        and moves it to another location in the road trip.
    """

    agent_genome = list(agent_genome)

    start_index = random.randint(0, len(agent_genome) - 1)
    length = random.randint(2, 20)

    genome_subset = agent_genome[start_index:start_index + length]
    agent_genome = agent_genome[:start_index] + agent_genome[start_index + length:]

    insert_index = random.randint(0, len(agent_genome) + len(genome_subset) - 1)
    agent_genome = agent_genome[:insert_index] + genome_subset + agent_genome[insert_index:]

    return tuple(agent_genome)

def generate_random_population(pop_size,all_waypoints):
    """
        Generates a list with `pop_size` number of random road trips.
    """

    random_population = []
    for agent in range(pop_size):
        random_population.append(generate_random_agent(all_waypoints))
    return random_population

def run_genetic_algorithm(all_waypoints,waypoint_distances,generations=5000, population_size=100):
    """
        The core of the Genetic Algorithm.

        `generations` and `population_size` must be a multiple of 10.
    """
    final_sequence = []
    population_subset_size = int(population_size / 10.)
    generations_10pct = int(generations / 10.)

    # Create a random population of `population_size` number of solutions.
    population = generate_random_population(population_size,all_waypoints)

    # For `generations` number of repetitions...
    for generation in range(generations):

        # Compute the fitness of the entire current population
        population_fitness = {}

        for agent_genome in population:
            if agent_genome in population_fitness:
                continue

            population_fitness[agent_genome] = compute_fitness(agent_genome,waypoint_distances)

        # Take the top 10% shortest road trips and produce offspring each from them
        new_population = []
        for rank, agent_genome in enumerate(sorted(population_fitness,
                                                   key=population_fitness.get)[:population_subset_size]):

            if (generation % generations_10pct == 0 or generation == generations - 1) and rank == 0:
                print("Generation %d best: %d | Unique genomes: %d" % (generation,
                                                                       population_fitness[agent_genome],
                                                                       len(population_fitness)))
                print(agent_genome)
                final_sequence = agent_genome
                print("")

            # Create 1 exact copy of each of the top road trips
            new_population.append(agent_genome)

            # Create 2 offspring with 1-3 point mutations
            for offspring in range(2):
                new_population.append(mutate_agent(agent_genome, 3))

            # Create 7 offspring with a single shuffle mutation
            for offspring in range(7):
                new_population.append(shuffle_mutation(agent_genome))

        # Replace the old population with the new population of offspring
        for i in range(len(population))[::-1]:
            del population[i]

        population = new_population
    return final_sequence




'''
CALL THIS FUNCTION FROM YOUR CODE
'''
def getHamiltonian(all_waypoints):
    '''
    INPUT > List of waypoints. Example-["A","B","C"]

    OUTPUT> complete polyline (string)
            total distance (number)
            total duration (number)
            optimized sequence of waypoints ("B","A","C")
    '''
    complete_polyline=""
    total_distance=0
    total_duration=0
    all_coordinates=[]

    polyline_dict = gatherData(all_waypoints)
    all_waypoints,waypoint_distances,waypoint_durations = readData()
    seq = run_genetic_algorithm(all_waypoints,waypoint_distances,generations=500, population_size=20)

    for i in range(len(seq)-1):
        complete_polyline += polyline_dict[frozenset([seq[i], seq[i+1]])]
        total_distance += waypoint_distances[frozenset([seq[i], seq[i+1]])]
        total_duration += waypoint_durations[frozenset([seq[i], seq[i+1]])]


    all_coordinates.extend(fp.decode(complete_polyline))
    #return total_distance,total_duration,seq
    return all_coordinates


'''
USE THIS FOR TESTING

print(getHamiltonian(["Mumbai","Delhi","Agra","Nagpur","Pune","Kalyan"]))
'''
