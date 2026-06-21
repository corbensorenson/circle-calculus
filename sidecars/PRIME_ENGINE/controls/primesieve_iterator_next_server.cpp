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

struct NextRequest {
  uint64_t start = 0;
  uint64_t repetitions = 1;
  uint64_t shift = 0;
  bool shifted = false;
};

void skip_spaces(const char** cursor)
{
  while (**cursor == ' ' || **cursor == '\t')
    (*cursor)++;
}

bool at_line_end(const char* cursor)
{
  while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n')
    cursor++;
  return *cursor == '\0';
}

bool parse_u64_field(const char** cursor, uint64_t* value)
{
  skip_spaces(cursor);
  if (**cursor == '-')
    return false;
  errno = 0;
  char* end = nullptr;
  unsigned long long parsed = std::strtoull(*cursor, &end, 10);
  if (errno != 0 || end == *cursor || parsed > std::numeric_limits<uint64_t>::max())
    return false;
  *cursor = end;
  *value = static_cast<uint64_t>(parsed);
  return true;
}

bool parse_request(const char* raw, NextRequest* request)
{
  const char* cursor = raw;
  skip_spaces(&cursor);
  *request = NextRequest{};

  if (std::strncmp(cursor, "shifted", 7) == 0 && (cursor[7] == ' ' || cursor[7] == '\t')) {
    cursor += 7;
    request->shifted = true;
    if (!parse_u64_field(&cursor, &request->repetitions) || request->repetitions == 0)
      return false;
    if (!parse_u64_field(&cursor, &request->shift))
      return false;
    if (!parse_u64_field(&cursor, &request->start))
      return false;
    return at_line_end(cursor);
  }

  if (!parse_u64_field(&cursor, &request->start))
    return false;
  skip_spaces(&cursor);
  if (!at_line_end(cursor)) {
    if (!parse_u64_field(&cursor, &request->repetitions) || request->repetitions == 0)
      return false;
    if (!at_line_end(cursor))
      return false;
  }
  return true;
}

bool request_start_at(const NextRequest& request, uint64_t index, uint64_t* start)
{
  if (!request.shifted) {
    *start = request.start;
    return true;
  }
  const uint64_t max = std::numeric_limits<uint64_t>::max();
  if (request.shift != 0 && index > max / request.shift)
    return false;
  uint64_t offset = request.shift * index;
  if (request.start > max - offset)
    return false;
  *start = request.start + offset;
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

      NextRequest request;
      if (!parse_request(line, &request)) {
        std::cerr << "request must be a u64 START value, START COUNT, or shifted COUNT SHIFT START\n";
        return 2;
      }

      for (uint64_t index = 0; index < request.repetitions; index++) {
        uint64_t start = 0;
        if (!request_start_at(request, index, &start)) {
          std::cerr << "shifted next-prime request overflowed u64\n";
          return 2;
        }
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
