#pragma once

#include <unistd.h>

namespace Color {

inline bool enabled() {
    static const bool e = (::isatty(STDOUT_FILENO) != 0);
    return e;
}

inline const char* reset()      { return enabled() ? "\033[0m"   : ""; }
inline const char* bold()       { return enabled() ? "\033[1m"   : ""; }
inline const char* dim()        { return enabled() ? "\033[2m"   : ""; }
inline const char* red()        { return enabled() ? "\033[31m"  : ""; }
inline const char* green()      { return enabled() ? "\033[32m"  : ""; }
inline const char* yellow()     { return enabled() ? "\033[33m"  : ""; }
inline const char* blue()       { return enabled() ? "\033[34m"  : ""; }
inline const char* magenta()    { return enabled() ? "\033[35m"  : ""; }
inline const char* cyan()       { return enabled() ? "\033[36m"  : ""; }
inline const char* bold_red()    { return enabled() ? "\033[1;31m" : ""; }
inline const char* bold_green()  { return enabled() ? "\033[1;32m" : ""; }
inline const char* bold_yellow() { return enabled() ? "\033[1;33m" : ""; }
inline const char* bold_cyan()   { return enabled() ? "\033[1;36m" : ""; }
inline const char* bold_blue()   { return enabled() ? "\033[1;34m" : ""; }

} // namespace Color
