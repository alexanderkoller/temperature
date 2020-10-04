import math
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.operators import desc_op
from tables import *
from flask import request
from flask import render_template
from bokeh.plotting import figure
from bokeh.embed import components
from scipy import stats
import numpy as np
from datetime import timedelta
import configparser
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# read config
config = configparser.ConfigParser()
config.read('server.ini')

# start DB engine
engine = create_engine(config["database"]["url"])
Session = sessionmaker(bind=engine)


app = Flask(__name__)

@app.route('/init')
def init():
    session = Session()
    meta = Metadatum(timestamp=func.now())
    session.add(meta)
    session.commit()
    return str(meta.id)

@app.route('/post_temperature', methods=['POST'])
def post_measurement():
    session = Session()
    data = float(request.args["temp"])
    id = int(request.args["id"])
    meast = Measurement(temperature=data, measurement_run=id, timestamp=func.now())
    session.add(meast)
    session.commit()
    return "hallo"

@app.route("/")
def index():
    target_temperature = 37.0

    session = Session()
    meta = session.query(Metadatum).order_by(desc_op(Metadatum.id)).first()
    id = meta.id
    # id=24

    # get measurements
    measurements = session.query(Measurement).filter(Measurement.measurement_run == id).order_by(Measurement.id).all()
    y = [a.temperature for a in measurements]
    x = [a.timestamp for a in measurements]

    # linear regression
    a_y = np.array(y)
    start_pos = np.argmin(a_y)                                   # step of min temperature
    slope, intercept, _, _, _ = stats.linregress(range(start_pos, len(x)), a_y[start_pos:])
    regression_available = not math.isnan(intercept) and not math.isnan(slope)

    if regression_available:
        # temperature growth rate
        interval = (x[-1] - x[0])/(len(x)-1)                     # time per step [timedelta]
        steps_per_minute = timedelta(minutes=1) / interval       # intervals per minute [float]
        degrees_per_minute = slope * steps_per_minute

        # ETA to target temperature
        steps_to_37 = (target_temperature - intercept) / slope   # [steps (float)]
        eta = x[0] + interval*steps_to_37
    
    else:
        degrees_per_minute, eta = None, None

    # plot data
    plot = figure(plot_height=300, sizing_mode='scale_width', x_axis_type='datetime')
    plot.line(x, y, line_width=3)

    # decorate data
    plot.line([min(x),max(x)], [target_temperature, target_temperature], line_color='red', line_dash='dashed')      # horizontal line at 37 degrees

    if regression_available:
        plot.line([x[start_pos], x[-1]], [intercept+slope*start_pos, intercept+slope*(len(x)-1)])                   # regression line

    script, div = components(plot)
    return render_template('adminlte.html', metadata=meta, temp=y[-1], eta=eta, degrees_per_minute=degrees_per_minute, plots=[(script,div)])


if __name__ == '__main__':
    port=int(config["server"]["port"])

    if "true" == config["server"]["tornado"].lower():
        print("Running with Tornado server ...")
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()

    else:
        print("Running with Flask server ...")
        app.run(debug=True, host='0.0.0.0', port=port)

