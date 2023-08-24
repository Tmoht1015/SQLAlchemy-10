# Import the dependencies.
import numpy as np
import re
import datetime as dt
from datetime import datetime #tried importing this for strptime for the dynamic portion, really struggled hard

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
db1 = automap_base()  
db1.prepare(engine, reflect=True)
measurement = db1.classes.measurement  
station = db1.classes.station
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return "Welcome to the Homepage!"

@app.route('/api/v1.0/routes')
def available_routes():
    routes = [
        '/api/v1.0/precipitation',
        '/api/v1.0/stations',
        '/api/v1.0/tobs',
        '/api/v1.0/2016-08-23',              
        '/api/v1.0/2016-08-23/2017-08-23'    
    ]
    return jsonify(routes)

@app.route('/api/v1.0/precipitation')
def get_precipitation():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    past_year = dt.datetime.strptime(recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= past_year).all()
    prcp_dict = {date: prcp for date, prcp in precipitation_data}
    session.close()
    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def get_stations():
    session = Session(engine)
    stations = session.query(station.station).all()
    station_list = [station[0] for station in stations]
    session.close()
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def get_temperature_obs():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    past_year = dt.datetime.strptime(recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)
    most_active_station = session.query(measurement.station).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    temperature_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= past_year).all()
    
    temp_data_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
    
    session.close()
    return jsonify(temp_data_list)

@app.route('/api/v1.0/2016-08-23')
def get_temperature_stats_start():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    start = '2016-08-23'  
    temperature_stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    if temperature_stats[0][0] is not None:
        stats = {
            'start_date': start,
            'end_date': recent_date,
            'TMIN': temperature_stats[0][0],
            'TAVG': temperature_stats[0][1],
            'TMAX': temperature_stats[0][2]
        }
        return jsonify(stats)
    else:
        return jsonify({'error': 'No temperature data available for the provided date range'})

@app.route('/api/v1.0/2016-08-23/2017-08-23')
def get_temperature_stats_start_end():
    session = Session(engine)
    start = datetime.strptime('2016-08-23', '%Y-%m-%d').date()
    end = datetime.strptime('2017-08-23', '%Y-%m-%d').date()
    
    print("Start Date:", start)
    print("End Date:", end)
    
    temperature_stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    if temperature_stats[0][0] is not None:
        stats = {
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'TMIN': temperature_stats[0][0],
            'TAVG': temperature_stats[0][1],
            'TMAX': temperature_stats[0][2]
        }
        return jsonify(stats)
    else:
        return jsonify({'error': 'No temperature data available for the provided date range'})

if __name__ == '__main__':
    app.run(debug=True)
