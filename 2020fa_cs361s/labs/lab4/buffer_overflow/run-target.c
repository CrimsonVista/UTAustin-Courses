#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "util.h"

#define USAGE "Usage: run-target [targetnum] [groupid]\n"
#define NUMTARGETS 2
#define MAXGROUPID 9999

#define MAXCOOKIE 32768
#define COOKIEPREFIX "COOKIE="

int main(int argc, char *argv[])
{

  if (argc != 3)
    error(USAGE);

  
  int targetnum;

  targetnum = atoi(argv[1]);
  if (targetnum < 1 || targetnum > NUMTARGETS)
    error(USAGE);


  int groupid;

  groupid = atoi(argv[2]);
  if (groupid < 0 || groupid > MAXGROUPID)
    error(USAGE);


  int cookielen;

  srand(groupid);
  cookielen = rand() % MAXCOOKIE + strlen(COOKIEPREFIX);


  char *cookiestr;

  if (NULL == (cookiestr = malloc(cookielen + 1)))
    error("Could not malloc cookie string\n");

  memset(cookiestr, 'X', cookielen);
  cookiestr[cookielen] = '\0';  /* NUL termination */
  memcpy(cookiestr, COOKIEPREFIX, strlen(COOKIEPREFIX));

  char target[20];
  if (0 > snprintf(target, sizeof(target), "target%d", targetnum))
    error("Could not print target name\n");

  char *args[] = { target, NULL };
  char *env[]  = { cookiestr, NULL };

  execve(target, args, env);
  /* not reached except in case of error */
  error("Could not exec target\n");
  return 1;
}
