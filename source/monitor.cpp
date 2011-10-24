#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
	if(argc < 2)
	{
		printf("At least 2 arguments are required. Usage: %s <commands...>", argv[0]);
		return 1;
	}

	char fullCommand[1024] = "";
	char space[2] = " ";

	for(int i = 1; i < argc; i++)
	{
		strcat(fullCommand, argv[i]);
		strcat(fullCommand, space);
	}

	char envString[1060] = "";
	sprintf(envString, "python monitor.py %s", fullCommand);

	system(envString);

	return 0;
}