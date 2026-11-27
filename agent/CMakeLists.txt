cmake_minimum_required(VERSION 3.21)
project(bibliotheque LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Bibliothèque commune
add_library(bibliotheque_core STATIC
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

set_target_properties(bibliotheque_core PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)

# Programme console
add_executable(bibliotheque main.cpp)
target_link_libraries(bibliotheque PRIVATE bibliotheque_core)

# Avertissements du compilateur
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
target_compile_options(bibliotheque PRIVATE -Wall -Wextra -Wpedantic)