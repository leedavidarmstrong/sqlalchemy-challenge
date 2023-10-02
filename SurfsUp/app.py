# Import necessary libraries
from flask import Flask, jsonify
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create a Flask app
app = Flask(__name__)

# Create an engine and establish a connection to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Define the routes

# Home route
@app.route("/")
def home():
    """List all available routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of precipitation data."""
    # Create a session to interact with the database
    session = Session(engine)
    
    try:    
        # Calculate the date one year from the last date in the data set
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
        
        # Query precipitation data for the last 12 months
        precipitation_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= one_year_ago).all()
        
        # Convert the query results to a dictionary
        precipitation_data_dict = {date: prcp for date, prcp in precipitation_data}
        
        # Return the JSON representation
        return jsonify(precipitation_data_dict)
    finally:
        # Close the database session when done
        session.close()

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Create a session to interact with the database
    session = Session(engine)
    
    try:
        # Query station data
        stations_data = session.query(Station.station).all()
        
        # Convert the query results to a list
        stations_list = [station[0] for station in stations_data]
        
        # Return the JSON list of stations
        return jsonify(stations_list)
    finally:
        # Close the database session when done
        session.close()

# Temperature Observations (TOBS) route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the most active station."""
    # Create a session to interact with the database
    session = Session(engine)
    
    try:
        # Find the most active station
        most_active_station = session.query(Measurement.station).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).first()[0]
        
        # Calculate the date one year from the last date in the data set
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
        
        # Query TOBS data for the last 12 months for the most active station
        tobs_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago).all()
        
        # Create a DataFrame from the query results
        tobs_df = pd.DataFrame(tobs_data, columns=['Date', 'TOBS'])
        
        # Convert the DataFrame to a list of dictionaries
        tobs_list = tobs_df.to_dict(orient='records')
        
        # Return the JSON list of temperature observations
        return jsonify(tobs_list)
    finally:
        # Close the database session when done
        session.close()

# Temperature statistics route (start date only)
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return a JSON list of temperature statistics (TMIN, TAVG, TMAX) for a start date."""
    # Create a session to interact with the database
    session = Session(engine)
    
    try:
        # Query temperature statistics for the specified start date
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        # Create a dictionary with temperature statistics
        temp_stats_start_data = {
            "TMIN": temperature_data[0][0],
            "TAVG": temperature_data[0][1],
            "TMAX": temperature_data[0][2]
        }
        
        # Return the JSON list of temperature statistics
        return jsonify(temp_stats_start_data)
    finally:
        # Close the database session when done
        session.close()

# Temperature statistics route (start and end dates)
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return a JSON list of temperature statistics (TMIN, TAVG, TMAX) for a start-end date range."""
    # Create a session to interact with the database
    session = Session(engine)
    
    try:
        # Query temperature statistics for the specified date range
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        
        # Create a dictionary with temperature statistics
        temp_stats_start_end_data = {
            "TMIN": temperature_data[0][0],
            "TAVG": temperature_data[0][1],
            "TMAX": temperature_data[0][2]
        }
        
        # Return the JSON list of temperature statistics
        return jsonify(temp_stats_start_end_data)
    finally:
        # Close the database session when done
        session.close()

# Run the app if this file is executed
if __name__ == "__main__":
    app.run(debug=True)

# Close the database session when the app is done
session.close()