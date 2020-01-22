/*
    Tuning
 */
static const char* version = "1.3";

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "tinypot_process.h"

#define INVALID_SOCKET (-1)
#define MAX(a,b) \
    ((a) > (b) ? (a) : (b))

typedef struct
{
    int port_num;
    int fd;
}
Record;

int main (int argc, char* argv[])
{
    fd_set master_fds;
    int socketFD;
    int port_num;
    int index;
    char* address_arg;
    int con_num;
    int iarg;
    Record* record;
    int num_ports;
    int maxfd = -1;

    printf ("Program tinypot version %s\n", version);

    address_arg = "";
    switch (argc)
    {
    case 1:
    case 2:
        fprintf (stderr, "Usage: tinypot [address|-] portnum portnum ...\n");
	exit (EXIT_FAILURE);
        break;
    default:
        address_arg = argv[1];
        break;
    }

    if (strcmp (address_arg, "-") == 0)
    {
        address_arg = "*";
    }
    num_ports = argc - 2;
    if ((record = (Record*)malloc (num_ports * sizeof (Record))) == NULL)
    {
        perror ("malloc failed");
	exit (EXIT_FAILURE);
    }

    if (signal (SIGPIPE, SIG_IGN) == SIG_ERR)
    {
        perror ("signal failed");
	exit (EXIT_FAILURE);
    }
    if (signal (SIGTRAP, SIG_IGN) == SIG_ERR)
    {
        perror ("signal failed");
	exit (EXIT_FAILURE);
    }

    FD_ZERO (&master_fds);
    for (iarg = 2 ; iarg < argc ; ++iarg)
    {
	char* port_arg = argv[iarg];
	struct sockaddr_in sa;
	if (sscanf (port_arg, "%d", &port_num) != 1)
	{
	    fprintf (stderr, "Illegal numeric expression \"%s\"\n", port_arg);
	    exit (EXIT_FAILURE);
	}
	socketFD = socket (PF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (socketFD == -1)
	{
	    perror ("cannot create socket");
	    exit (EXIT_FAILURE);
	}

	memset (&sa, 0, sizeof (sa));
	sa.sin_family = AF_INET;
	sa.sin_port = htons ((uint16_t)port_num);

	if (strcmp (address_arg, "*") == 0)
	    sa.sin_addr.s_addr = htonl (INADDR_ANY);
	else
	    sa.sin_addr.s_addr = inet_addr (address_arg);

	if (bind (socketFD, (struct sockaddr *)(&sa), (socklen_t)sizeof (sa))
	    == -1)
	{
	    fprintf (stderr, "On port %d, ", port_num);
	    perror ("bind failed");
	    exit (EXIT_FAILURE);
	}

	if (listen (socketFD, 10) == -1)
	{
	    perror ("listen failed");
	    exit (EXIT_FAILURE);
	}
	FD_SET (socketFD, &master_fds);
	maxfd = MAX (maxfd, socketFD);
	record[iarg-2].port_num = port_num;
	record[iarg-2].fd = socketFD;
    }

    printf ("%s Listening on address %s, %d TCP/IP ports:\n",
        my_time(), address_arg, num_ports);
    printf ("    ");
    for (index = 0 ; index < num_ports ; ++index)
        printf (" %d", record[index].port_num);
    printf ("\n");
    fflush (stdout);

    for (con_num = 1 ; ; ++con_num)
    {
	int status;
	fd_set read_fds = master_fds;

	status = select (maxfd+1, &read_fds, NULL, NULL, NULL);
	if (status < 0)
	{
	    perror ("select failed");
	    continue;
	}
	socketFD = INVALID_SOCKET;
	for (index = 0 ; index < num_ports ; ++index)
	{
	    if (FD_ISSET (record[index].fd, &read_fds))
	    {
	        socketFD = record[index].fd;
		port_num = record[index].port_num;
		break;
	    }
	}
	if (socketFD == INVALID_SOCKET)
	{
	    fprintf (stderr, "%s: spurious connection\n", my_time());
	    fflush (stderr);
	    continue;
	}

	if (process_connection (con_num, port_num, socketFD) != 0)
	    break;
    }

    return EXIT_SUCCESS;
}
