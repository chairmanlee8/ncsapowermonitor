#include "powermon.h"

void powermon_config(powermon_config_t* pcfg, char* fn)
{
	/*
		Reads a file with filename "fn" and fills a powermon_config_t struct with the
		parsed data. Not a real JSON parser, just a reduced one.
	*/

	FILE *fp = fopen(fn, "r");
	if(!fp) return;

	int cin = 0;
	char buffer[256] = "";
	char dest[256] = "";
	int buf_index = 0, dest_index = 0;
	int state = 0;	// states are 0-discarding, 1-buffering, 2-expecting rval, 3-dest loading
	int state_ivar = 0;

	while((cin = fgetc(fp)) != EOF)
	{
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
				else if((char)cin == '{')
				{
					if(!strcmp(buffer, "instance_variables")) state_ivar = 1;
				}
				break;
			case 3:
				if((char)cin == '\"') 
				{
					dest[dest_index++] = '\0';

					if(!strcmp(buffer, "db_host")) strcpy(pcfg->db_host, buffer);
					else if(!strcmp(buffer, "db_port")) pcfg->db_port = atoi(buffer);
					else if(!strcmp(buffer, "db_username")) strcpy(pcfg->db_username, buffer);
					else if(!strcmp(buffer, "db_password")) strcpy(pcfg->db_password, buffer);
					else if(!strcmp(buffer, "db_database")) strcpy(pcfg->db_database, buffer);
					else if(!strcmp(buffer, "keep_alive_interval")) pcfg->keep_alive = atoi(buffer);
					else if(!strcmp(buffer, "collect_host")) strcpy(pcfg->host, buffer);
					else if(!strcmp(buffer, "collect_port")) pcfg->port = atoi(buffer);

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
}

void powermon_start(powermon_config_t* pcfg)
{
	/*
		Notify host to start power monitoring.
	*/
}

void powermon_mark(powermon_config_t* pcfg, char* mark_name, int mark_type)
{
	/*
		Send mark to host.
	*/
}

void powermon_stop(powermon_config_t* pcfg)
{
	/*
		Notify host to stop power monitoring.
	*/
}

void powermon_ping_thread(void* pcfg)
{
	/*
		Thread which pings host at interval keep_alive / 2.
	*/
}