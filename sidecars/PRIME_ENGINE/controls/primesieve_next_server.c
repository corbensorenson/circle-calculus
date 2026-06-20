#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <primesieve.h>

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

int main(void)
{
  char line[128];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    uint64_t start = 0;
    uint64_t repetitions = 1;
    if (!parse_request(line, &start, &repetitions)) {
      fprintf(stderr, "request must be a u64 START value or START COUNT\n");
      return 2;
    }

    for (uint64_t index = 0; index < repetitions; index++) {
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
