#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "powermon.h"

int main(int argc, char* argv[])
{
	if(argc < 2)
	{
		printf("At least 2 arguments are required. Usage: %s <commands...>", argv[0]);
		return 1;
	}

	// argv[1] should be config file
	powermon_config_t power_config = {0};
	powermon_config(&power_config, argv[1]);

	printf("Configuration details:\n");
	printf("db_host = %s\n", power_config.db_host);
	printf("db_port = %d\n", power_config.db_port);
	printf("db_username = %s\n", power_config.db_username);
	printf("db_password = %s\n", power_config.db_password);
	printf("db_database = %s\n", power_config.db_database);
	printf("keep_alive = %d\n", power_config.keep_alive);
	printf("host = %s\n", power_config.host);
	printf("port = %d\n", power_config.port);
	printf("job_owner = %s\n", power_config.job_owner);
	printf("job_id = %s\n", power_config.job_id);
	printf("job_process = %s\n", power_config.job_process);

	return 0;
}