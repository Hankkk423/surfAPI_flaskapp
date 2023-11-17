from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler
from datetime import datetime

from CWA_API.Tide.getCwaTideApI import fetch_cwa_tide_data, getThreeDays



app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application
print("app.py running")


@app.route('/')
@cross_origin()  # Enable CORS for this specific route
def index():
    # do something...
    return 'Surf API flask app'


@app.route('/test', methods=['POST'])
@cross_origin()  # Enable CORS for this specific route
def test():
    message = request.json['message']
    response = '[Port: /test] success'
    print('Prot: /test, Get: ', message)
    tag = 'test'
    return jsonify({'res': response, 'tag': tag})


@app.route('/cwa_api/tide_chart', methods=['POST'])
@cross_origin()  # Enable CORS for this specific route
def cwa_tide_chart():
    message = request.json['message']
    response = getThreeDays(message)  # message is "LocationId"
    return jsonify({'res': response})



# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
scheduler.api_enabled = True
scheduler.init_app(app)

# Interval example
@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=1800)
def job1():
    print(f'Job 1 executed at {datetime.now()}')

# Cron example for running every day at 2 pm (14:00)
@scheduler.task('cron', id='daily_job_1', hour=16, minute=6)
def daily_job_1():
    print(f'Daily Job executed at {datetime.now()}')
    fetch_cwa_tide_data()

# New cron example for running every day at 3 pm (15:00)
@scheduler.task('cron', id='daily_job_2', hour=15, minute=00)
def daily_job_2():
    print(f'Another Daily Job executed at {datetime.now()}')
    # Call the function you want to execute
    # e.g., fetch_another_data()



if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True)
