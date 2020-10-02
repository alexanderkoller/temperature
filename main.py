from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm.session import sessionmaker
from tables import *
from flask import request
from flask import render_template
from bokeh.plotting import figure
from bokeh.embed import components

engine = create_engine('sqlite+pysqlite3:///data.db')
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
    session = Session()
    id = session.query(func.max(Metadatum.id)).scalar()

    measurements = session.query(Measurement).filter(Measurement.measurement_run == id).order_by(Measurement.id).all()
    y = [x.temperature for x in measurements]
    # x = list(range(len(y)))
    x = [a.timestamp for a in measurements]

    plot = figure(plot_height=300, sizing_mode='scale_width', x_axis_type='datetime')
    plot.line(x, y, line_width=4)
    plot.line([min(x),max(x)], [37,37], line_color='red', line_dash='dashed')
    script, div = components(plot)

    return render_template('template.html', id=id, plots=[(script,div)])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

