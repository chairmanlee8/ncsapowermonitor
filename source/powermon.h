#ifndef __POWERMON_H
#define __POWERMON_H

typedef struct
{
	char	index[256];
	char	value[256];
	void*	next_entry;
} dict_t;

typedef struct
{
	char	db_host[256];
	int		db_port;
	char	db_username[256]; 
	char	db_password[256];
	char	db_database[256];
	int		keep_alive;
	char	host[256];
	int		port;
	char	job_owner[256];
	char	job_id[256];
	char	job_process[256];
} powermon_config_t;

void powermon_config(powermon_config_t* pcfg, char* fn);
int powermon_start(powermon_config_t* pcfg);
int powermon_mark(powermon_config_t* pcfg, char* mark_name, int mark_type);
int powermon_stop(powermon_config_t* pcfg);

#endif