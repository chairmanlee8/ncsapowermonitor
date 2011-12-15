from flask import Flask, url_for, render_template, make_response, g	

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

def connect_db():
	return MySQLdb.connect(host=DATABASE_HOST, port=DATABASE_PORT, db=DATABASE_NAME, user=DATABASE_USER, passwd=DATABASE_PASS)

app = Flask(__name__)

@app.before_request
def before_request():
	g.db = connect_db()
	g.cur = g.db.cursor()
	pass

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'cur'): g.cur.close()
	if hasattr(g, 'db'): g.db.close()

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/<int:guid>")
def view_job(guid):
	# Detail view for a job
	return render_template('view_job.html', guid=guid)

@app.route("/jobs/all")
def jobs_all():
	g.cur.execute('SELECT * FROM job_data ORDER BY job_started DESC')
	rows = g.cur.fetchall()

	return json.dumps(rows, default=dthandler)
	
@app.route("/jobs/<int:guid>")
def jobs_data(guid):
	# Get job data
	g.cur.execute('SELECT UNIX_TIMESTAMP(job_started), job_host, job_owner, job_id, job_process FROM job_data WHERE guid = %s', (guid,))
	job = g.cur.fetchall()

	# Get markers for this job_id
	g.cur.execute('SELECT time_unix, time_ms, name, marker_type FROM marker_data WHERE guid = %s ORDER BY time_unix ASC, time_ms ASC', (guid,))
	markers = g.cur.fetchall()

	time_start = 0
	time_end = 0
	
	if len(markers) < 2:
		time_start = int(job[0][0])
		time_end = int(job[0][0]) + 1000
	else:
		time_start = int(markers[0][0])
		time_end = int(markers[-1][0])
	
	# Get data for job_id between marker extremes
	g.cur.execute('SELECT device_sensor, time_unix, time_ms, amperage FROM power_data WHERE time_unix >= %s AND time_unix <= %s ORDER BY device_sensor ASC, time_unix ASC', (time_start, time_end))
	data = g.cur.fetchall()

	# Get configuration data
	g.cur.execute('SELECT device_sensor, voltage, description FROM conf_data_sensor WHERE guid = %s ORDER BY device_sensor ASC', (guid,))
	configs = g.cur.fetchall()
	
	# Return data in JSON form
	return json.dumps({'data': data, 'config': configs, 'markers': markers, 'job': job[0]})

@app.route("/jobs/csv/<int:guid>")
def jobs_data_csv(guid):
	# Get job data
	g.cur.execute('SELECT UNIX_TIMESTAMP(job_started), job_host, job_owner, job_id, job_process FROM job_data WHERE guid = %s', (guid,))
	job = g.cur.fetchall()

	# Get markers for this job_id
	g.cur.execute('SELECT time_unix, time_ms, name, marker_type FROM marker_data WHERE guid = %s ORDER BY time_unix ASC, time_ms ASC', (guid,))
	markers = g.cur.fetchall()

	time_start = 0
	time_end = 0
	
	if len(markers) < 2:
		time_start = int(job[0][0])
		time_end = int(job[0][0]) + 1000
	else:
		time_start = int(markers[0][0])
		time_end = int(markers[-1][0])
	
	# Get data for job_id between marker extremes
	g.cur.execute('SELECT device_sensor, time_unix, time_ms, amperage FROM power_data WHERE time_unix >= %s AND time_unix <= %s ORDER BY device_sensor ASC, time_unix ASC', (time_start, time_end))
	data = g.cur.fetchall()

	# Get configuration data
	g.cur.execute('SELECT device_sensor, voltage, description FROM conf_data_sensor WHERE guid = %s ORDER BY device_sensor ASC', (guid,))
	configs = g.cur.fetchall()

	csv_string = "\"UNIX Time\",\"mA\",\"Volts\"\r\n"
	for config_row in configs:
		csv_string += "%s\r\n" % (config_row[0])
		for data_row in data:
			if data_row[0] == config_row[0]:
				csv_string += "%f,%d,%d\r\n" % (float(data_row[1]) + float(data_row[2])/1000.0, data_row[3], config_row[1])

	response = make_response(csv_string)
	response.headers['Content-Type'] = 'text/csv'
	response.headers['Content-Disposition'] = 'attachment;filename=%d.csv' % guid

	return response
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080, debug=True)