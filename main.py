from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm.session import sessionmaker
from tables import *
from flask import request

engine = create_engine('sqlite+pysqlite3:///data.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

@app.route('/init')
def init():
    meta = Metadatum(timestamp=func.now())
    session.add(meta)
    session.commit()
    return str(meta.id)

@app.route('/post_temperature', methods=['POST'])
def post_measurement():
    print(request.args)
    data = float(request.args["temp"])
    id = int(request.args["id"])
    meast = Measurement(temperature=data, measurement_run=id, timestamp=func.now())
    session.add(meast)
    session.commit()
    return "hallo"

@app.route("/")
def index():
    return "hallo"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

