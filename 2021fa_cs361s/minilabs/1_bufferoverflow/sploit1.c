#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"
#include "shellcode.h"

#define PIPEPATH "/tmp/t1pipe"

int main(void)
{
  writecmd(PIPEPATH, "Hello, target1!");
  
  return 0;
}
