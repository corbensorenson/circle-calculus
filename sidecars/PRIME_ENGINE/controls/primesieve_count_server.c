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

static int parse_i32(const char* raw, int* value)
{
  errno = 0;
  char* end = NULL;
  long parsed = strtol(raw, &end, 10);
  if (errno != 0 || end == raw || parsed < 0 || parsed > INT32_MAX)
    return 0;
  while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')
    end++;
  if (*end != '\0')
    return 0;
  *value = (int) parsed;
  return 1;
}

int main(void)
{
  char line[192];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    char* first_raw = strtok(line, " \t\r\n");
    uint64_t repetitions = 1;
    char* low_raw = first_raw;
    if (first_raw != NULL && strcmp(first_raw, "repeat") == 0) {
      char* repetitions_raw = strtok(NULL, " \t\r\n");
      if (repetitions_raw == NULL || !parse_u64(repetitions_raw, &repetitions) ||
          repetitions == 0) {
        fprintf(stderr, "repeat request must be: repeat COUNT LOW HIGH_EXCLUSIVE THREADS\n");
        return 2;
      }
      low_raw = strtok(NULL, " \t\r\n");
    }
    char* high_raw = strtok(NULL, " \t\r\n");
    char* threads_raw = strtok(NULL, " \t\r\n");
    char* extra = strtok(NULL, " \t\r\n");
    if (low_raw == NULL || high_raw == NULL || threads_raw == NULL || extra != NULL) {
      fprintf(stderr, "request must be: LOW HIGH_EXCLUSIVE THREADS or repeat COUNT LOW HIGH_EXCLUSIVE THREADS\n");
      return 2;
    }

    uint64_t low = 0;
    uint64_t high = 0;
    int threads = 0;
    if (!parse_u64(low_raw, &low) || !parse_u64(high_raw, &high) ||
        !parse_i32(threads_raw, &threads)) {
      fprintf(stderr, "LOW/HIGH must be u64 and THREADS must be nonnegative i32\n");
      return 3;
    }
    if (high <= low) {
      fprintf(stderr, "range must be nonempty and half-open: LOW < HIGH_EXCLUSIVE\n");
      return 4;
    }

    if (threads > 0)
      primesieve_set_num_threads(threads);

    for (uint64_t index = 0; index < repetitions; index++) {
      errno = 0;
      uint64_t count = primesieve_count_primes(low, high - 1);
      if (count == PRIMESIEVE_ERROR && errno == EDOM) {
        fprintf(stderr, "primesieve_count_primes failed for [%" PRIu64 ", %" PRIu64 ")\n",
                low, high);
        return 5;
      }

      printf("%" PRIu64 "\n", count);
    }
    fflush(stdout);
  }
  return 0;
}
