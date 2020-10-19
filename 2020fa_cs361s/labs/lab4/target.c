#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"

#define PIPEPATH "/tmp/targetpipe"

void overflow(void)
{
  char buf[127];
  readcmd(PIPEPATH, buf, 32768);
}

int main(void)
{
  if (NULL == getenv("COOKIE"))
    error("Run target using run-target\n");
  overflow();
  
  return 0;
}
