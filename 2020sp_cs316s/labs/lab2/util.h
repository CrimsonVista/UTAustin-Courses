/* does not return */
void error(const char *msg);

#define RWX_REGION_SIZE 4096
/* allocates an RWX_REGION_SIZE-byteslong region marked RWX  */
char *allocate_rwx(void);

/* reads from pipe up to (and including) bufsize or EOF */
void readcmd(const char *path, char *cmdbuf, int bufsize);

/* writes cmd to pipe up to NUL byte*/
void writecmd(const char *path, const char *cmd);

/* writes numbytes of cmd to pipe, possibly including NUL bytes */
void writecmdbytes(const char *path, const char *cmd, int numbytes);
