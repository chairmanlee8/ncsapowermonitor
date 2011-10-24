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
	char* dest = 0;
	int buf_index = 0;
	int state = 0;	// states are 0-discarding, 1-buffering, 2-expecting rval, 3-dest loading

	while((cin = fgetc(fp)) != EOF)
	{
		switch(state)
		{
			case 0:
				if((char)cin == '\"')
				{
					
				}
				break;
			case 1:
				break;
			case 2:
				break;
			case 3:
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