#ifndef __POWERMON_H
#define __POWERMON_H

#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <stdio.h>

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
	dict_t	*instance_variables;
} powermon_config_t;

#endif