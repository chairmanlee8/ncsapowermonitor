from flask import Flask, url_for, render_template	

import MySQLdb
import json
import datetime

# from http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

DATABASE_HOST = "acm"
DATABASE_PORT = 3306
DATABASE_NAME = "power"
DATABASE_USER = "poweradmin"
DATABASE_PASS = "power"

db = MySQLdb.connect(host=DATABASE_HOST, port=DATABASE_PORT, db=DATABASE_NAME, user=DATABASE_USER, passwd=DATABASE_PASS)
cur = db.cursor()

app = Flask(__name__)

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/<int:guid>")
def view_job(guid):
	# Detail view for a job
	return render_template('view_job.html', guid=guid)

@app.route("/jobs/all")
def jobs_all():
	cur.execute('SELECT * FROM job_data ORDER BY job_started DESC')
	rows = cur.fetchall()

	return json.dumps(rows, default=dthandler)
	
@app.route("/jobs/<int:guid>")
def jobs_data(guid):
	# Get job data
	cur.execute('SELECT UNIX_TIMESTAMP(job_started), job_host, job_owner, job_id, job_process FROM job_data WHERE guid = %s', (guid,))
	job = cur.fetchall()

	# Get markers for this job_id
	cur.execute('SELECT time_unix, time_ms, name, marker_type FROM marker_data WHERE guid = %s ORDER BY time_unix ASC', (guid,))
	markers = cur.fetchall()

	time_start = 0
	time_end = 0
	
	if len(markers) < 2:
		time_start = int(job[0][0])
		time_end = int(job[0][0]) + 1000
	else:
		time_start = int(markers[0][0])
		time_end = int(markers[-1][0])
	
	# Get data for job_id between marker extremes
	cur.execute('SELECT device_sensor, time_unix, time_ms, amperage FROM power_data WHERE time_unix >= %s AND time_unix <= %s ORDER BY device_sensor ASC, time_unix ASC', (time_start, time_end))
	data = cur.fetchall()

	# Get configuration data
	cur.execute('SELECT device_sensor, voltage, description FROM conf_data_sensor WHERE guid = %s ORDER BY device_sensor ASC', (guid,))
	configs = cur.fetchall()
	
	# Return data in JSON form
	return json.dumps({'data': data, 'config': configs, 'markers': markers, 'job': job[0]})
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080, debug=True)