#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include "util.h"

#define USAGE "Usage: run-target [fd-pad] [groupid]\n"
#define MAXFDPAD 32
#define MAXGROUPID 9999

#define MAXCOOKIE 32768
#define COOKIEPREFIX "COOKIE="

int main(int argc, char *argv[])
{

  if (argc != 3)
    error(USAGE);

  int fdpad;

  fdpad = atoi(argv[1]);
  if (fdpad < 0 || fdpad > MAXFDPAD)
    error(USAGE);

  int groupid;

  groupid = atoi(argv[2]);
  if (groupid < 0 || groupid > MAXGROUPID)
    error(USAGE);


  int cookielen;

  srand(groupid); (void)rand();
  cookielen = MAXCOOKIE + (rand() % MAXCOOKIE) + strlen(COOKIEPREFIX);


  char *cookiestr;

  if (NULL == (cookiestr = malloc(cookielen + 1)))
    error("Could not malloc cookie string\n");

  memset(cookiestr, 'X', cookielen);
  cookiestr[cookielen] = '\0';  /* NUL termination */
  memcpy(cookiestr, COOKIEPREFIX, strlen(COOKIEPREFIX));

  char target[] = "target";

  char *args[] = { target, NULL };
  char *env[]  = { cookiestr, NULL };

  int i;
  for (i = 0; i < fdpad; i++)
    if (-1 == open("/dev/null", O_RDONLY))
      error("Failed to pad file descriptors.\n");

  execve(target, args, env);
  /* not reached except in case of error */
  error("Could not exec target\n");
  return 1;
}
