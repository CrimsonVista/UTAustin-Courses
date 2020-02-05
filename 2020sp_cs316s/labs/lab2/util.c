#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include "util.h"

/* does not return */
void error(const char *msg)
{
  fputs(msg, stderr);
  exit(EXIT_FAILURE);
}

/* allocates a region marked RWX, RWX_REGION_SIZE bytes long */
char *allocate_rwx(void)
{
  void *r;

  if (MAP_FAILED == (r = mmap(NULL, RWX_REGION_SIZE,
                              PROT_READ | PROT_WRITE | PROT_EXEC,
                              MAP_ANON | MAP_SHARED, -1, 0)))
    error("Failed to allocate rwx page");

  return r;
}

/* reads from pipe up to EOF or newline */
void readcmd(const char *path, char *cmdbuf, int bufsize)
{
  FILE *pipefile;
  size_t n;

  if (bufsize < 2)
    error("Buffer is to small to read into\n");
  if (NULL == (pipefile = fopen(path, "r")))
    error("Failed to open pipe -- did you run 'make pipes'?\n");
  n = fread(cmdbuf, 1, bufsize-1, pipefile);
  if (0 != ferror(pipefile))
    error("Failed to read from pipe\n");
  cmdbuf[n] = '\0';             /* fread does not NUL-terminate */
  if (EOF == fclose(pipefile))
    error("Failed to close pipe\n");
}

/* writes cmd to pipe */
void writecmd(const char *path, const char *cmd)
{
  FILE *pipefile;
  if (NULL == (pipefile = fopen(path, "w")))
    error("Failed to open pipe -- did you run 'make pipes'?\n");
  if (EOF == (fputs(cmd, pipefile)))
    error("Failed to write to pipe\n");
  if (EOF == fclose(pipefile))
    error("Failed to close pipe\n");
}

/* writes numbytes of cmd to pipe, possibly including NUL bytes */
void writecmdbytes(const char *path, const char *cmd, int numbytes)
{
  FILE *pipefile;

  if (0 > numbytes)
    error("Cannot write a negative number of bytes.\n");
  if (NULL == (pipefile = fopen(path, "w")))
    error("Failed to open pipe -- did you run 'make pipes'?\n");
  if (numbytes > fwrite(cmd, 1, numbytes, pipefile))
    error("Failed to write to pipe\n");
  if (EOF == fclose(pipefile))
    error("Failed to close pipe\n");
}
