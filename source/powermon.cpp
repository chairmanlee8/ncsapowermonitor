#include "powermon.h"

#include <sys/types.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

pthread_t death_timer;

int powermon_config(powermon_config_t* pcfg, char* fn)
{
	/*
		Reads a file with filename "fn" and fills a powermon_config_t struct with the
		parsed data. Not a real JSON parser, just a reduced one.
	*/

	FILE *fp = fopen(fn, "r");
	if(!fp) {
		fprintf(stderr, "Failed to open configuration file.\n");
		return 1;
	}

	int cin = 0;
	char buffer[256] = "";
	char dest[256] = "";
	int buf_index = 0, dest_index = 0;
	int state = 0;	// states are 0-discarding, 1-buffering, 2-expecting rval, 3-dest loading

	while((cin = fgetc(fp)) != EOF)
	{
		if((char)cin == '{' || (char)cin == '}')
		{
			state = 0;
			buf_index = 0;
			dest_index = 0;
		}

		switch(state)
		{
			case 0:
				if((char)cin == '\"')
				{
					state = 1;
					buf_index = 0;
				}
				break;
			case 1:
				if((char)cin == '\"')
				{
					buffer[buf_index++] = '\0';
					state = 2;
				}
				else
					buffer[buf_index++] = (char)cin;
				break;
			case 2:
				if((char)cin == '\"')
				{
					state = 3;
					dest_index = 0;
				}
				break;
			case 3:
				if((char)cin == '\"') 
				{
					dest[dest_index++] = '\0';

					if(!strcmp(buffer, "db_host")) strcpy(pcfg->db_host, dest);
					else if(!strcmp(buffer, "db_port")) pcfg->db_port = atoi(dest);
					else if(!strcmp(buffer, "db_username")) strcpy(pcfg->db_username, dest);
					else if(!strcmp(buffer, "db_password")) strcpy(pcfg->db_password, dest);
					else if(!strcmp(buffer, "db_database")) strcpy(pcfg->db_database, dest);
					else if(!strcmp(buffer, "keep_alive_interval")) pcfg->keep_alive = atoi(dest);
					else if(!strcmp(buffer, "collect_host")) strcpy(pcfg->host, dest);
					else if(!strcmp(buffer, "collect_port")) pcfg->port = atoi(dest);
					else if(!strcmp(buffer, "job_owner")) strcpy(pcfg->job_owner, dest);
					else if(!strcmp(buffer, "job_id")) strcpy(pcfg->job_id, dest);
					else if(!strcmp(buffer, "job_process")) strcpy(pcfg->job_process, dest);

					state = 0;
				}
				else
					dest[dest_index++] = (char)cin;
				break;
			default:
				break;
		}
	}

	fclose(fp);
	return 0;
}

int send_tcp_message(powermon_config_t* pcfg, const char* message)
{
	int status, sd;
	struct addrinfo hints;
	struct addrinfo *servinfo;
	char buffer[33];

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;

	sprintf(buffer, "%d", pcfg->port);

	if((status = getaddrinfo(pcfg->host, buffer, &hints, &servinfo)) != 0)
		return status;

	sd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

	if(connect(sd, servinfo->ai_addr, servinfo->ai_addrlen) == -1)
		return -1;

	send(sd, message, strlen(message), 0);
	recv(sd, (void*)&message[0], sizeof(message), 0);

	close(sd);
	freeaddrinfo(servinfo);

	return 0;
}

int send_udp_message(powermon_config_t* pcfg, const char* message)
{
	int status, sd;
	struct addrinfo hints;
	struct addrinfo *servinfo;
	char buffer[33];

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_DGRAM;

	sprintf(buffer, "%d", pcfg->port);

	if((status = getaddrinfo(pcfg->host, buffer, &hints, &servinfo)) != 0)
		return status;

	sd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

	sendto(sd, message, strlen(message), 0, servinfo->ai_addr, servinfo->ai_addrlen);

	close(sd);
	freeaddrinfo(servinfo);

	return 0;
}

void* powermon_ping_thread(void* pcfg)
{
	/*
		Thread which pings host at interval keep_alive / 2.
	*/

	while(1)
	{
		send_tcp_message((powermon_config_t*) pcfg, "ping");
		sleep(((powermon_config_t*) pcfg)->keep_alive / 2);
	}

	return 0;
}

int powermon_start(powermon_config_t* pcfg)
{
	/*
		Notify host to start power monitoring.
	*/

	char message[1024];
	char job_host[256];

	gethostname(job_host, 256);
	sprintf(message, "start;%s;%s;%s;%s", job_host, getenv(pcfg->job_owner), getenv(pcfg->job_id), getenv(pcfg->job_process));

	int result = send_tcp_message(pcfg, message);

	if(result != 0)
		return result;

	// Start death timer
	pthread_create(&death_timer, NULL, powermon_ping_thread, (void*) pcfg);

	return 0;
}

int powermon_mark(powermon_config_t* pcfg, const char* mark_name, int mark_type)
{
	/*
		Send mark to host.
	*/

	char message[1024];
	sprintf(message, "mark;%s;%d", mark_name, mark_type);
	return send_udp_message(pcfg, message);
}

int powermon_stop(powermon_config_t* pcfg)
{
	/*
		Notify host to stop power monitoring.
	*/

	return send_tcp_message(pcfg, "stop");
}