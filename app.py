import base64
import io
import sqlite3
import os
from flask import Flask, jsonify, redirect, render_template, request
from main import get_cities_weather_data, show_current_weather, show_graph, get_data_for_correlation
import matplotlib.pyplot as plt
from database.script import main, create_connection


app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))


@app.route('/', methods=['POST', 'GET'])
def index():
    global cities
    cities = get_cities_weather_data()
    return render_template('index.html', cities=cities)


@app.route('/plot', methods=['POST'])
def plot():
    city_name = request.form["button"]
    global forecast_graph
    forecast_graph = show_graph(city_name=city_name)
    global df
    df = show_current_weather(city_name=city_name)
    global correlation_graph
    correlation_graph = get_data_for_correlation(city_name=city_name)
    return render_template('index.html', cities=cities, forecast_graph=forecast_graph, dataframe=df.to_html(index=False), correlation_graph=correlation_graph)


@app.route('/save_graph', methods=['POST'])
def save_graph():
    base64_img = request.form["forecast_graph"]
    save_graph_to_database(base64_img)
    return redirect('/display_graph')


@app.route('/display_graph', methods=['GET'])
def display_graph():
    database = r"weather_db.db"
    graph_bytes = retrieve_graph_from_database(database)

    if graph_bytes is not None:
        graph_base64 = base64.b64encode(graph_bytes).decode('utf-8')
        return render_template('graph.html', graph_base64=graph_base64)
    else:
        return "No graph found in the database."


def retrieve_graph_from_database(db_file):
    conn = create_connection(db_file)

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT graph FROM graphs ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result is not None:
            graph_bytes = result[0]
            return graph_bytes

    conn.close()
    return None


def save_graph_to_database(graph_base64):
    # Convert base64 string to bytes
    graph_bytes = base64.b64decode(graph_base64)


    database = r"weather_db.db"

    conn = main(database)


    # Insert the graph into the database
    if conn is not None:
        conn.execute('INSERT INTO graphs (graph) VALUES (?)', (graph_bytes,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()





app.run(host='0.0.0.0', port=port)
