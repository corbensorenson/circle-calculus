#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <primecount.h>

static int parse_request(const char* raw, uint64_t* start, uint64_t* repetitions)
{
  errno = 0;
  char* end = NULL;
  unsigned long long parsed_start = strtoull(raw, &end, 10);
  if (errno != 0 || end == raw)
    return 0;

  while (*end == ' ' || *end == '\t')
    end++;

  unsigned long long parsed_repetitions = 1;
  if (*end != '\0' && *end != '\r' && *end != '\n') {
    errno = 0;
    char* repetition_end = NULL;
    parsed_repetitions = strtoull(end, &repetition_end, 10);
    if (errno != 0 || repetition_end == end || parsed_repetitions == 0)
      return 0;
    end = repetition_end;
    while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')
      end++;
    if (*end != '\0')
      return 0;
  } else {
    while (*end == '\r' || *end == '\n')
      end++;
    if (*end != '\0')
      return 0;
  }

  *start = (uint64_t) parsed_start;
  *repetitions = (uint64_t) parsed_repetitions;
  return 1;
}

static int parse_i32(const char* raw, int* value)
{
  errno = 0;
  char* end = NULL;
  long parsed = strtol(raw, &end, 10);
  if (errno != 0 || end == raw || parsed < 0 || parsed > INT_MAX)
    return 0;
  while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')
    end++;
  if (*end != '\0')
    return 0;
  *value = (int) parsed;
  return 1;
}

static int64_t next_prime_at_or_above(uint64_t start)
{
  int64_t pi_before_start = 0;
  if (start > 2) {
    if (start - 1 > (uint64_t) INT64_MAX) {
      errno = ERANGE;
      return -1;
    }
    pi_before_start = primecount_pi((int64_t) (start - 1));
    if (pi_before_start < 0)
      return -1;
  }

  if (pi_before_start == INT64_MAX) {
    errno = ERANGE;
    return -1;
  }
  return primecount_nth_prime(pi_before_start + 1);
}

int main(int argc, char** argv)
{
  if (argc > 2) {
    fprintf(stderr, "usage: primecount-next-server [THREADS]\n");
    return 2;
  }
  if (argc == 2) {
    int threads = 0;
    if (!parse_i32(argv[1], &threads)) {
      fprintf(stderr, "THREADS must be a nonnegative i32\n");
      return 2;
    }
    if (threads > 0)
      primecount_set_num_threads(threads);
  }

  char line[128];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    uint64_t start = 0;
    uint64_t repetitions = 1;
    if (!parse_request(line, &start, &repetitions)) {
      fprintf(stderr, "request must be a u64 START value or START COUNT\n");
      return 3;
    }

    for (uint64_t index = 0; index < repetitions; index++) {
      errno = 0;
      int64_t prime = next_prime_at_or_above(start);
      if (prime < 0) {
        fprintf(stderr, "primecount pi+nth-prime failed for START=%" PRIu64 "\n", start);
        return 4;
      }
      printf("%" PRId64 "\n", prime);
    }
    fflush(stdout);
  }
  return 0;
}
