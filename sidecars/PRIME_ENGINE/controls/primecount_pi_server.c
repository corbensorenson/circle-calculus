#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <primecount.h>

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

static int64_t checked_pi(uint64_t n)
{
  if (n > (uint64_t) INT64_MAX) {
    errno = ERANGE;
    return -1;
  }
  return primecount_pi((int64_t) n);
}

int main(void)
{
  char line[192];
  while (fgets(line, sizeof(line), stdin) != NULL) {
    if (strcmp(line, "quit\n") == 0 || strcmp(line, "exit\n") == 0)
      break;

    char* first_raw = strtok(line, " \t\r\n");
    uint64_t repetitions = 1;
    uint64_t shift = 0;
    int shifted = 0;
    char* low_raw = first_raw;
    if (first_raw != NULL && strcmp(first_raw, "repeat") == 0) {
      char* repetitions_raw = strtok(NULL, " \t\r\n");
      if (repetitions_raw == NULL || !parse_u64(repetitions_raw, &repetitions) ||
          repetitions == 0) {
        fprintf(stderr, "repeat request must be: repeat COUNT LOW HIGH_EXCLUSIVE THREADS\n");
        return 2;
      }
      low_raw = strtok(NULL, " \t\r\n");
    } else if (first_raw != NULL && strcmp(first_raw, "shifted") == 0) {
      shifted = 1;
      char* repetitions_raw = strtok(NULL, " \t\r\n");
      char* shift_raw = strtok(NULL, " \t\r\n");
      if (repetitions_raw == NULL || shift_raw == NULL ||
          !parse_u64(repetitions_raw, &repetitions) || repetitions == 0 ||
          !parse_u64(shift_raw, &shift)) {
        fprintf(stderr, "shifted request must be: shifted COUNT SHIFT LOW HIGH_EXCLUSIVE THREADS\n");
        return 2;
      }
      low_raw = strtok(NULL, " \t\r\n");
    }
    char* high_raw = strtok(NULL, " \t\r\n");
    char* threads_raw = strtok(NULL, " \t\r\n");
    char* extra = strtok(NULL, " \t\r\n");
    if (low_raw == NULL || high_raw == NULL || threads_raw == NULL || extra != NULL) {
      fprintf(stderr, "request must be: LOW HIGH_EXCLUSIVE THREADS, repeat COUNT LOW HIGH_EXCLUSIVE THREADS, or shifted COUNT SHIFT LOW HIGH_EXCLUSIVE THREADS\n");
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
    if (high - 1 > (uint64_t) INT64_MAX) {
      fprintf(stderr, "primecount C API helper supports HIGH_EXCLUSIVE-1 <= INT64_MAX\n");
      return 5;
    }

    if (threads > 0)
      primecount_set_num_threads(threads);

    for (uint64_t index = 0; index < repetitions; index++) {
      uint64_t request_low = low;
      uint64_t request_high = high;
      if (shifted) {
        if (shift != 0 && index > UINT64_MAX / shift) {
          fprintf(stderr, "shifted request offset overflowed u64\n");
          return 7;
        }
        uint64_t offset = shift * index;
        if (low > UINT64_MAX - offset || high > UINT64_MAX - offset) {
          fprintf(stderr, "shifted request range overflowed u64\n");
          return 7;
        }
        request_low = low + offset;
        request_high = high + offset;
      }
      if (request_high - 1 > (uint64_t) INT64_MAX) {
        fprintf(stderr, "primecount C API helper supports HIGH_EXCLUSIVE-1 <= INT64_MAX\n");
        return 5;
      }
      errno = 0;
      int64_t high_count = checked_pi(request_high - 1);
      int64_t low_count = request_low > 0 ? checked_pi(request_low - 1) : 0;
      if (high_count < 0 || low_count < 0 || high_count < low_count) {
        fprintf(stderr, "primecount_pi diff failed for [%" PRIu64 ", %" PRIu64 ")\n",
                request_low, request_high);
        return 6;
      }

      printf("%" PRId64 "\n", high_count - low_count);
    }
    fflush(stdout);
  }
  return 0;
}
