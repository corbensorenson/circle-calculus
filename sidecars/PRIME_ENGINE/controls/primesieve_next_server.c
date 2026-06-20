#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <primesieve.h>

static int parse_u64(const char* raw, uint64_t* value)
{
  errno = 0;
  char* end = NULL;
  unsigned long long parsed = strtoull(raw, &end, 10);
  if (errno != 0 || end == raw)
    return 0;
  while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')
    end++;
  if (*end != '\0')
    return 0;
  *value = (uint64_t) parsed;
  return 1;
}

int main(void)
{
  char line[128];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    uint64_t start = 0;
    if (!parse_u64(line, &start)) {
      fprintf(stderr, "request must be a u64 START value\n");
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
    fflush(stdout);
  }
  return 0;
}
