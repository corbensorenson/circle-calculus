#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <primesieve.h>

typedef struct {
  uint64_t start;
  uint64_t repetitions;
  uint64_t shift;
  int shifted;
} NextRequest;

static void skip_spaces(const char** cursor)
{
  while (**cursor == ' ' || **cursor == '\t')
    (*cursor)++;
}

static int at_line_end(const char* cursor)
{
  while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n')
    cursor++;
  return *cursor == '\0';
}

static int parse_u64_field(const char** cursor, uint64_t* value)
{
  skip_spaces(cursor);
  if (**cursor == '-')
    return 0;
  errno = 0;
  char* end = NULL;
  unsigned long long parsed = strtoull(*cursor, &end, 10);
  if (errno != 0 || end == *cursor || parsed > UINT64_MAX)
    return 0;
  *cursor = end;
  *value = (uint64_t) parsed;
  return 1;
}

static int parse_request(const char* raw, NextRequest* request)
{
  const char* cursor = raw;
  skip_spaces(&cursor);
  request->start = 0;
  request->repetitions = 1;
  request->shift = 0;
  request->shifted = 0;

  if (strncmp(cursor, "shifted", 7) == 0 && (cursor[7] == ' ' || cursor[7] == '\t')) {
    cursor += 7;
    request->shifted = 1;
    if (!parse_u64_field(&cursor, &request->repetitions) || request->repetitions == 0)
      return 0;
    if (!parse_u64_field(&cursor, &request->shift))
      return 0;
    if (!parse_u64_field(&cursor, &request->start))
      return 0;
    return at_line_end(cursor);
  }

  if (!parse_u64_field(&cursor, &request->start))
    return 0;
  skip_spaces(&cursor);
  if (!at_line_end(cursor)) {
    if (!parse_u64_field(&cursor, &request->repetitions) || request->repetitions == 0)
      return 0;
    if (!at_line_end(cursor))
      return 0;
  }
  return 1;
}

static int request_start_at(const NextRequest* request, uint64_t index, uint64_t* start)
{
  if (!request->shifted) {
    *start = request->start;
    return 1;
  }
  if (request->shift != 0 && index > UINT64_MAX / request->shift)
    return 0;
  uint64_t offset = request->shift * index;
  if (request->start > UINT64_MAX - offset)
    return 0;
  *start = request->start + offset;
  return 1;
}

int main(void)
{
  char line[128];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    NextRequest request;
    if (!parse_request(line, &request)) {
      fprintf(stderr, "request must be a u64 START value, START COUNT, or shifted COUNT SHIFT START\n");
      return 2;
    }

    for (uint64_t index = 0; index < request.repetitions; index++) {
      uint64_t start = 0;
      if (!request_start_at(&request, index, &start)) {
        fprintf(stderr, "shifted next-prime request overflowed u64\n");
        return 2;
      }
      uint64_t* primes = (uint64_t*) primesieve_generate_n_primes(1, start, UINT64_PRIMES);
      if (primes == NULL) {
        fprintf(stderr, "primesieve_generate_n_primes failed for START=%" PRIu64 "\n", start);
        return 3;
      }

      uint64_t prime = primes[0];
      primesieve_free(primes);
      printf("%" PRIu64 "\n", prime);
    }
    fflush(stdout);
  }
  return 0;
}
