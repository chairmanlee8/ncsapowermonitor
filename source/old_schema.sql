CREATE TABLE job_data
(
	guid			BIGINT,
	job_started		TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	job_host		VARCHAR(256),
	job_owner		VARCHAR(256),
	job_id			VARCHAR(256),
	job_process		VARCHAR(256),
	PRIMARY KEY (guid)
);

CREATE TABLE power_data
(
	device_sensor	VARCHAR(32),
	time_unix		BIGINT,
	time_ms			SMALLINT,
	amperage		FLOAT
);

CREATE TABLE marker_data
(
	guid			BIGINT,
	time_unix		BIGINT,
	time_ms			SMALLINT,
	name			VARCHAR(64),
	marker_type		SMALLINT,
	FOREIGN KEY (guid) REFERENCES job_data(guid)
);

CREATE TABLE conf_data_sensor
(
	guid			BIGINT,
	device_sensor	VARCHAR(32),
	voltage			FLOAT,
	description		VARCHAR(1024),
	FOREIGN KEY (guid) REFERENCES job_data(guid)
);