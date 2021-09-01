#include <err.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sysexits.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define PCRE2_CODE_UNIT_WIDTH 8
#include "pcre2.h"

static char *password;
static char *secret;
static pcre2_code *put_pattern;
static pcre2_code *get_pattern;
static pcre2_match_data *match_data;

static void *safe_realloc(void *p, size_t size)
{
	void *ret = realloc(p, size);
	if (!ret)
		free(p);
	return ret;
}

static char *find_crnl(const char *str, size_t n)
{
	while (--n)
	{
		if (str[0] == '\r' && str[1] == '\n')
			return (char *)str;
		++str;
	}
	return 0;
}

static pcre2_code *compile_re(const char *pattern)
{
	PCRE2_SIZE erroffset;
	int errorcode;
	pcre2_code *re = pcre2_compile((PCRE2_SPTR)pattern, -1, 0, &errorcode, &erroffset, 0);
	if (re == 0)
	{
		PCRE2_UCHAR8 buffer[120];
		pcre2_get_error_message(errorcode, buffer, 120);
		errx(EX_SOFTWARE, "regex: %s", buffer);
	}
	return re;
}

/* Read until \r\n is encountered, the buffer is filled, or the
 * receive end of the connection is closed). Return the amount of data
 * read. Anything after the \r\n is discarded. */
static ssize_t recv_line(int sock, char *buffer, size_t buffer_size)
{
	size_t size = 0;
	while (size < buffer_size)
	{
		ssize_t amount = recv(sock, buffer, buffer_size + size, 0);
		if (amount < 0)
		{
			if (errno == EINTR)
				continue;
			return -1;
		}
		if (amount == 0)
			break; /* Connection closed. */
		char *crnl = find_crnl(buffer, amount);
		if (crnl)
		{
			size += crnl - buffer;
			break;
		}
		size += amount;
		buffer += amount;
	}
	return size;
}

/* Send a line. */
static int send_line(int sock, const char *buffer, size_t size)
{
	while (size)
	{
		ssize_t amount = send(sock, buffer, size, 0);
		if (amount < 0)
		{
			if (errno == EINTR)
				continue;
			return -1;
		}
		buffer += amount;
		size -= amount;
	}
	return 0;
}

void handle_connection(int sock)
{
	char buffer[1024];
	ssize_t size = recv_line(sock, buffer, sizeof buffer);

	if (size < 0)
		return;

	/* Match strings. */
	int rc = pcre2_match(put_pattern, (PCRE2_SPTR)buffer, size, 0, 0, match_data, 0);
	if (rc > 0)
	{
		PCRE2_SIZE *ovector = pcre2_get_ovector_pointer(match_data);
		size_t password_size = ovector[3] - ovector[2];
		size_t secret_size = ovector[5] - ovector[4];
		password = safe_realloc(password, password_size + 1);
		secret = safe_realloc(secret, secret_size + 1);
		memcpy(password, buffer + ovector[2], password_size);
		password[password_size] = 0;
		memcpy(secret, buffer + ovector[4], secret_size);
		secret[secret_size] = 0;
		strcpy(buffer, "SECRET STORED\r\n");
	}
	else if ((rc = pcre2_match(get_pattern, (PCRE2_SPTR)buffer, size, 0, 0, match_data, 0)) > 0)
	{
		PCRE2_SIZE *ovector = pcre2_get_ovector_pointer(match_data);
		size_t password_size = ovector[3] - ovector[2];
		if (password && !strncmp(password, buffer + ovector[2], password_size))
			snprintf(buffer, sizeof buffer, "SECRET: %s\r\n", secret);
		else
			strcpy(buffer, "SORRY\r\n");
	}
	else
	{
		strcpy(buffer, "INVALID COMMAND\r\n");
	}

	/* Send the response. */
	send_line(sock, buffer, strlen(buffer));
}

int main(int argc, char *argv[])
{
	if (argc != 2)
		errx(EX_USAGE, "Usage: %s PORT\n", argv[0]);

	char *end;
	unsigned long port = strtoul(argv[1], &end, 10);
	if (port >= 0x10000 || argv[0][0] == 0 || *end != 0)
		errx(EX_USAGE, "Invalid port: %s\n", argv[1]);

	/* Create a socket to accept connections from localhost. */
	int listen_fd = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (listen_fd == -1)
		err(EX_OSERR, "socket");

	if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &(int) { 1 }, sizeof(int)) == -1)
		err(EX_OSERR, "setsockopt(SO_REUSEADDR)");

	struct sockaddr_in saddr =
	{
		.sin_port = htons(port),
		.sin_addr = { .s_addr = inet_addr("127.0.0.1") },
		.sin_family = AF_INET,
	};

	if (bind(listen_fd, (struct sockaddr *)&saddr, sizeof(saddr)) == -1)
		err(EX_OSERR, "bind");

	if (listen(listen_fd, SOMAXCONN) == -1)
		err(EX_OSERR, "listen");

	/* Compile some regular expressions. */
	put_pattern = compile_re("^PUT SECRET\\s+(\\S+)\\s+(.*)");
	get_pattern = compile_re("^GET SECRET\\s+(\\S+)");
	match_data = pcre2_match_data_create(20, 0);

	while (1)
	{
		int sock = accept(listen_fd, 0, 0);
		if (sock == -1)
			err(EX_OSERR, "accept");
		handle_connection(sock);
		close(sock);
	}
}
