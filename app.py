import base64
import io
import sqlite3
from flask import Flask, jsonify, render_template, request
from main import get_cities_weather_data, show_current_weather, show_graph, get_data_for_correlation
import matplotlib.pyplot as plt


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    global cities
    cities = get_cities_weather_data()
    return render_template('index.html', cities=cities)


@app.route('/plot', methods=['POST'])
def plot():
    city_name = request.form["button"]
    forecast_graph = show_graph(city_name=city_name)
    df = show_current_weather(city_name=city_name)
    correlation_graph = get_data_for_correlation(city_name=city_name)
    return render_template('index.html', cities=cities, forecast_graph=forecast_graph, dataframe=df.to_html(index=False), correlation_graph=correlation_graph)
