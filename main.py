
# Libraries
import base64
import io
import os
import re
import json
import folium
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
import scipy.stats
from geonamescache import GeonamesCache
from urllib.request import urlopen
from jinja2 import Environment, FileSystemLoader
from IPython.display import display, HTML, Javascript

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

api_key = "768d81e0c5c733e2a375488139b78bb0"

# Global variables to store the data
cities = []


def kelvin_to_celsius(kelvin):
    kelvin_celcius_delta = 273.15
    celsius = kelvin - kelvin_celcius_delta
    return celsius


# returns list of random cities
def get_random_cities(num_cities):
    gc = GeonamesCache()
    cities = list(gc.get_cities().values())

    random_cities = random.sample(cities, num_cities)
    city_names = [city['name'] for city in random_cities]

    return city_names


# getting lat and lon of random city
def get_geo_response(city):
    pattern = r"^(?!.*\s)[\x00-\x7F]+$"
    city_name = str(city)
    if re.match(pattern, city_name):
        baseGeoUrl = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
        try:
            geoResponse = urlopen(baseGeoUrl)
            return geoResponse
        except Exception as e:
            print(f"error while opening url: {str(e)}")
            return None

# get random cities with their coordinations
def get_cities_coords(num_cities):
    city_coords = []
    cities = get_random_cities(num_cities)
    for city in cities:
        city_response = get_geo_response(city)
        if city_response is not None:
            try:
                city_dict = {}
                city_orig = json.loads(city_response.read())
                geo_df = pd.DataFrame(city_orig)
                city_dict["lat"] = geo_df.loc[0, "lat"]
                city_dict["lon"] = geo_df.loc[0, "lon"]
                city_coords.append(city_dict)
            except Exception as e:
                print(f"Error occurred reading the response: {str(e)}")

    return city_coords

# return weather info of city
def get_weather_data_with_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    # Send a request to the API and retrieve weather data for the coordinates
    response = urlopen(url)
    weather_data = json.loads(response.read())
    # Check if a city name is available in the response
    city_dict = {}
    if "name" in weather_data:
        city_dict["city_name"] = weather_data["name"]
        city_dict["lat"] = weather_data["coord"]["lat"]
        city_dict["lon"] = weather_data["coord"]["lon"]
        city_dict["curr_temp"] = kelvin_to_celsius(weather_data["main"]["temp"])
        city_dict["max_temp"] = kelvin_to_celsius(weather_data["main"]["temp_max"])
        city_dict["min_temp"] = kelvin_to_celsius(weather_data["main"]["temp_min"])
        humidity = weather_data["main"]["humidity"]
        city_dict["humidity"] = f"{humidity}%"
        city_dict["sunrise"] = str(pd.to_datetime(weather_data["sys"]["sunrise"], unit="s"))
        city_dict["sunset"] = str(pd.to_datetime(weather_data["sys"]["sunset"], unit="s"))

    return city_dict

# trial and error mit der anzahl cities, gemäss docs gehen 60 calls/min mit dem free plan
def get_cities_weather_data():
    city_coords = get_cities_coords(10)
    global city_list
    city_list = []
    for city in city_coords:
        lat = city["lat"]
        lon = city["lon"]
        city_data = get_weather_data_with_coords(lat=lat, lon=lon)  # returns a dict
        if len(city_data) > 0:
            city_list.append(city_data)

    return city_list

#get forecast data from api for a specific city
def get_forecast_data_with_coords(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
    # Send a request to the API and retrieve forecast data for the coordinates
    response = urlopen(url)
    forecast_data = json.loads(response.read())
    return forecast_data

# return dataframe with weather data for city
def show_current_weather(city_name):
    city = next((c for c in city_list if c["city_name"] == city_name), None)
    if city is not None:
        curr_temp = city["curr_temp"]
        max_temp = city["max_temp"]
        min_temp = city["min_temp"]
        humidity = city["humidity"]
        sunrise = city["sunrise"]
        sunset = city["sunset"]

        # Create a DataFrame for the current weather information
        data = {
            "Current Temperature": [curr_temp],
            "Maximum Temperature": [max_temp],
            "Minimum Temperature": [min_temp],
            "Humidity": [humidity],
            "Sunrise": [sunrise],
            "Sunset": [sunset]
        }
        df = pd.DataFrame(data)

        # Display the DataFrame
        return df

# return plot for weather forecast
def show_graph(city_name):
    # Clear the current figure
    plt.figure()

    city = next((c for c in city_list if c["city_name"] == city_name), None)
    if city is not None:
        forecast_data = get_forecast_data_with_coords(city["lat"], city["lon"])["list"]

        # Extract the temperatures and datetimes from the forecast data
        temperatures = [data["main"]["temp"] for data in forecast_data]
        datetimes = [data["dt_txt"] for data in forecast_data]

        # Convert temperatures from Kelvin to Celsius
        temperatures_celsius = [kelvin_to_celsius(temp) for temp in temperatures]

        # Filter datetimes to show only two per day
        filtered_datetimes = []
        prev_date = None
        for dt in datetimes:
            date = dt.split()[0]  # Extract date from datetime string
            if date != prev_date:
                filtered_datetimes.append(dt)
                prev_date = date

        label = f"Temperature Forecast for {city_name}"
        x_label = "Time"
        y_label = "Temperature (Celsius)"
        x_values = list(range(len(temperatures_celsius)))  # Use index as x-values
        plt.plot(x_values, temperatures_celsius, label=label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(label)

        # Set x-axis tick labels to show only two timestamps per day
        num_datetimes = len(filtered_datetimes)
        x_ticks = np.linspace(0, len(temperatures_celsius) - 1, num_datetimes, dtype=int)
        plt.xticks(x_ticks, filtered_datetimes, rotation=45)

        plt.legend()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')

        buf.seek(0)
        forecast_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return forecast_base64

# correlation analysis
def get_data_for_correlation(city_name):
    city = next((c for c in city_list if c["city_name"] == city_name), None)
    if city is not None:
        forecast_data = get_forecast_data_with_coords(city["lat"], city["lon"])["list"]

        # Extract the temperatures and datetimes from the forecast data
        sea_levels = [data["main"]["sea_level"] for data in forecast_data]
        humidities = [data["main"]["humidity"] for data in forecast_data]

        # Create a DataFrame for the correlation analysis
        data = {
            "sea_level": sea_levels,
            "humidity": humidities
        }
        df = pd.DataFrame(data)
       
        correlation_graph = plot_linear_correlation(df)
        return correlation_graph


# return plot for linear correlation
def plot_linear_correlation(df):

    sea_levels = df["sea_level"]
    humidities = df["humidity"]
    slope, intercept, r, p, stderr = scipy.stats.linregress(sea_levels, humidities)

    # regression line
    line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, correlation coefficient={r:.2f}'

    # create plot
    fig, ax = plt.subplots()
    ax.plot(sea_levels, humidities, linewidth=0, marker='s', label='Data points')
    ax.plot(sea_levels, intercept + slope * sea_levels, label=line)
    ax.set_xlabel(df.keys()[0])
    ax.set_ylabel(df.keys()[1])
    ax.legend(facecolor="white")
    ax.set_title(label="correlation analysis")
    buf = io.BytesIO()
    fig.savefig(buf, format='png')

    buf.seek(0)
    correlation_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return correlation_base64
