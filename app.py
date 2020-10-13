from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from itertools import chain

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page. List all routes that are available.
@app.route("/")
def home():
    return (f"Available routes<br/>"
            f"/api/v1.0/precipitation : list dates and precipitation<br/>"
            f"/api/v1.0/stations : list all stations from dataset<br/>"
            f"/api/v1.0/tobs : list dates and temperature from a year from the last data point (2017-08-23)<br/>"
            f"/api/v1.0/startdate : show min, average and max temperature after specified start date<br/>"
            f"/api/v1.0/startdate/enddate : show min, average and max temperature between specified start and end date<br/><br/><br/>"
            f"Start and end date should be formatted as 'YYYY-MM-DD'")


# Convert the query results to a Dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()
    dict_prcp = dict(prcp_data)
    session.close()
    return jsonify(dict_prcp)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    return jsonify(stations)


# Query for the dates and temperature observations from a year from the last data point.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    year, month, day = map(int, last_date.split("-"))
    year_ago = datetime(year, month, day) - timedelta(days=365)
    year_ago = (year_ago.strftime("%Y-%m-%d"))

    # tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= "2016-08-23").all()
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    session.close()
    return jsonify(tobs)
    # return jsonify(last_date)

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_date(start):
    list = []
    session = Session(engine)
    temperature = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()
    for data in temperature:
        dict = {}
        dict['Date'] = data[0]
        dict['Tmin'] = data[1]
        dict['Tavg'] = round(data[2],2)
        dict['Tmax'] = data[3]
        list.append(dict)

    #Return a JSON list
    return jsonify(list)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date,  the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    list = []
    session = Session(engine)
    temperature = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()
    for data in temperature:
        dict = {}
        dict['Date'] = data[0]
        dict['Tmin'] = data[1]
        dict['Tavg'] = round(data[2],2)
        dict['Tmax'] = data[3]
        list.append(dict)

    #Return a JSON list
    return jsonify(list)

if __name__ == '__main__':
    app.run(debug=True)