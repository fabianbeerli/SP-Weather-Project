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

# This function serves as the main route of the web application. It sets up the initial state by initializing the database, retrieving weather data for cities, and fetching saved graphs from the database. 
# It then renders the 'index.html' template, passing the cities and saved graphs as variables to be displayed on the webpage. 
@app.route('/', methods=['POST', 'GET'])
def index():
    global database
    database = r"weather_db.db"
    global cities
    cities = get_cities_weather_data()
    saved_graphs = fetch_graphs_from_db()
    return render_template('index.html', cities=cities, saved_graphs=saved_graphs)

#  This function receives a POST request, calls several functions to generate and retrieve graph and weather data based on the selected city, 
#  and then renders the 'index.html' template with the cities, forecast graph, weather data, and correlation graph as variables to be displayed on the webpage
@app.route('/plot', methods=['POST'])
def plot():
    main(database)
    global city_name
    city_name = request.form["button"]
    global forecast_graph
    forecast_graph = show_graph(city_name=city_name)
    global df
    df = show_current_weather(city_name=city_name)
    global correlation_graph
    correlation_graph = get_data_for_correlation(city_name=city_name)
    return render_template('index.html', cities=cities, 
                           forecast_graph=forecast_graph, 
                           dataframe=df.to_html(index=False),
                            correlation_graph=correlation_graph
                        )

# This function receives a POST request containing a base64-encoded image of a graph, saves it to the database, and then redirects the user to the '/display_graph' route to view the saved graph
@app.route('/save_graph', methods=['POST'])
def save_graph():
    base64_img = request.form["forecast_graph"]
    save_graph_to_database(base64_img)
    return redirect('/display_graph')

# This function retrieves a graph from the database and displays it in a web page if found; otherwise, it returns a message indicating that no graph was found in the database
@app.route('/display_graph', methods=['GET'])
def display_graph():
    graph_bytes = retrieve_graph_from_database()

    if graph_bytes is not None:
        graph_base64 = base64.b64encode(graph_bytes).decode('utf-8')
        return render_template('graph.html', graph_base64=graph_base64)
    else:
        return "No graph found in the database."

# This function retrieves a saved graph from the database based on the provided graph ID and displays it in a web page
@app.route('/view_saved_graph/<int:graph_id>', methods=['GET'])
def view_saved_graph(graph_id):
    conn = create_connection(database)
    cursor = conn.cursor()
    query = "SELECT graph, city_name FROM graphs WHERE id = ?"
    cursor.execute(query, (graph_id,))
    result_graph = cursor.fetchone()

    if result_graph is not None:
        graph_bytes, city_name = result_graph
        graph_base64 = base64.b64encode(graph_bytes).decode('utf-8')
    else:
        return "No graph found in the database."
    
    cursor.close()
    conn.close()
    return render_template("graph.html", graph_base64=graph_base64)

# retieve graph from database
def retrieve_graph_from_database():
    conn = create_connection(database)

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT graph FROM graphs ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result is not None:
            graph_bytes = result[0]
            return graph_bytes

    conn.close()
    return None

# save graph to database
def save_graph_to_database(graph_base64):
    # Convert base64 string to bytes
    graph_bytes = base64.b64decode(graph_base64)

    conn = create_connection(database)

    # Insert the graph into the database
    if conn is not None:
        conn.execute('INSERT INTO graphs (graph, city_name) VALUES (?, ?)', (graph_bytes, city_name))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# fetch the graphs form the database
def fetch_graphs_from_db():
    conn = create_connection(database)

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT id, graph, city_name FROM graphs")
        result = cursor.fetchall()

        if result is not None:
            graph_list = []
            for row in result:
                graph_dict = {}
                graph_dict["id"] = row[0]
                graph_dict["graph"] = row[1]
                graph_dict["city_name"] = row[2]
                graph_list.append(graph_dict)
            return graph_list
        
    conn.close()
    return None


app.run(host='0.0.0.0', port=port)
