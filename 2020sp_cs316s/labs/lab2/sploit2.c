#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"
#include "shellcode.h"

#define PIPEPATH "/tmp/t2pipe"

int main(void)
{
  writecmd(PIPEPATH, "Hello, target2!");
  
  return 0;
}
