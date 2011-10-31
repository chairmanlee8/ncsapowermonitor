#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "powermon.h"

int main(int argc, char* argv[])
{
	if(argc < 2)
	{
		printf("At least 2 arguments are required. Usage: %s <configuration file> <commands...>", argv[0]);
		return 1;
	}

	powermon_config_t pcfg = {0};
	powermon_config(&pcfg, argv[1]);

	char fullCommand[1024] = "";
	char space[2] = " ";

	for(int i = 2; i < argc; i++)
	{
		strcat(fullCommand, argv[i]);
		strcat(fullCommand, space);
	}

	printf("Running with power monitoring enabled...\n");

	powermon_start(&pcfg);
	powermon_mark(&pcfg, "monitor", 0);

	system(fullCommand);

	powermon_mark(&pcfg, "monitor", 1);
	powermon_stop(&pcfg);
	
	printf("...done.\n");

	return 0;
}