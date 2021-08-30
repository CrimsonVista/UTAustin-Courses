#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"

#define PIPEPATH "/tmp/t1pipe"
static char *cmdbuf;

void overflow(void)
{
  char buf[127];
  strcpy(buf, cmdbuf);
}

int main(void)
{
  cmdbuf = allocate_rwx();
  readcmd(PIPEPATH, cmdbuf, RWX_REGION_SIZE);
  overflow();
  
  return 0;
}
