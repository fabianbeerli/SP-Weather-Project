from geonamescache import GeonamesCache
import random


# returns list of random cities
def getRandomCities(num_cities):
    gc = GeonamesCache()
    cities = list(gc.get_cities().values())

    random_cities = random.sample(cities, num_cities)
    city_names = [city['name'] for city in random_cities]

    return city_names