import math
from flask import Flask
import pytz
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
from pytz import timezone
from tzlocal import get_localzone

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

# Converts the given datetime from UTC to the local timezone.
def localize_timezone(dt):
    utc = pytz.timezone("UTC")
    dt_utc = utc.localize(dt)
    return dt_utc.astimezone(get_localzone())

def regression_since_minimum(x,y):
    a_y = np.array(y)
    start_pos = np.argmin(a_y)                                   # step of min temperature
    slope, intercept, _, _, _ = stats.linregress(range(start_pos, len(x)), a_y[start_pos:])
    return slope, intercept, start_pos

def regression_recent(x,y,recent_regression):
    a_y = np.array(y)
    start_pos = max(0, len(x)-recent_regression)   # start pos for the regression: look recent_regression many steps into the past
    slope, intercept, _, _, _ = stats.linregress(range(start_pos, len(x)), a_y[start_pos:])

    # but we want to plot the regression line from the time of the min value anyway
    start_pos = np.argmin(a_y)

    return slope, intercept, start_pos


@app.route("/")
def index():
    target_temperature = config.getfloat("analysis", "target_temperature", fallback=37.0)
    recent_regression = config.getint("analysis", "regression_recent", fallback=None)

    session = Session()
    meta = session.query(Metadatum).order_by(desc_op(Metadatum.id)).first()
    id = meta.id
    # id=40 

    # get measurements
    measurements = session.query(Measurement).filter(Measurement.measurement_run == id).order_by(Measurement.id).all()
    y = [a.temperature for a in measurements]
    x = [a.timestamp for a in measurements]

    # linear regression
    if recent_regression:
        slope, intercept, start_pos = regression_recent(x, y, recent_regression)
    else:
        slope, intercept, start_pos = regression_since_minimum(x,y)

    regression_available = np.isfinite(intercept) and np.isfinite(slope)    # checks that they are not nan and not infinity

    if regression_available:
        # temperature growth rate
        interval = (x[-1] - x[0])/(len(x)-1)                     # time per step [timedelta]
        steps_per_minute = timedelta(minutes=1) / interval       # intervals per minute [float]
        degrees_per_minute = slope * steps_per_minute            # convert growth rate per step to growth rate per minute

        # ETA to target temperature
        steps_to_37 = (target_temperature - intercept) / slope   # [steps (float)]
        eta = localize_timezone(x[0] + interval*steps_to_37) if slope > 0 else None
    
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
    start_time = localize_timezone(meta.timestamp)
    return render_template('adminlte.html', start_time=start_time, metadata=meta, temp=y[-1], eta=eta, degrees_per_minute=degrees_per_minute, plots=[(script,div)])


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

