#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <iostream>
#include <limits>

#include <primesieve.hpp>

namespace {

bool parse_request(const char* raw, uint64_t* start, uint64_t* repetitions)
{
  errno = 0;
  char* end = nullptr;
  unsigned long long parsed_start = std::strtoull(raw, &end, 10);
  if (errno != 0 || end == raw)
    return false;

  while (*end == ' ' || *end == '\t')
    end++;

  unsigned long long parsed_repetitions = 1;
  if (*end != '\0' && *end != '\r' && *end != '\n') {
    errno = 0;
    char* repetition_end = nullptr;
    parsed_repetitions = std::strtoull(end, &repetition_end, 10);
    if (errno != 0 || repetition_end == end || parsed_repetitions == 0)
      return false;
    end = repetition_end;
    while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n')
      end++;
    if (*end != '\0')
      return false;
  } else {
    while (*end == '\r' || *end == '\n')
      end++;
    if (*end != '\0')
      return false;
  }

  *start = static_cast<uint64_t>(parsed_start);
  *repetitions = static_cast<uint64_t>(parsed_repetitions);
  return true;
}

uint64_t stop_hint_for(uint64_t start)
{
  constexpr uint64_t hint_span = 1'000'000;
  const uint64_t max = std::numeric_limits<uint64_t>::max();
  return start > max - hint_span ? max : start + hint_span;
}

} // namespace

int main()
{
  try {
    primesieve::iterator iterator;
    char line[128];
    while (std::fgets(line, sizeof(line), stdin) != nullptr) {
      if (std::strcmp(line, "quit\n") == 0 || std::strcmp(line, "exit\n") == 0)
        break;

      uint64_t start = 0;
      uint64_t repetitions = 1;
      if (!parse_request(line, &start, &repetitions)) {
        std::cerr << "request must be a u64 START value or START COUNT\n";
        return 2;
      }

      for (uint64_t index = 0; index < repetitions; index++) {
        iterator.jump_to(start, stop_hint_for(start));
        std::cout << iterator.next_prime() << '\n';
      }
      std::cout.flush();
    }
  } catch (const std::exception& exc) {
    std::cerr << "libprimesieve iterator helper failed: " << exc.what() << '\n';
    return 3;
  }
  return 0;
}
