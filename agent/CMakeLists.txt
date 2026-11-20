cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

# Specifie qu'on veut la version C++17 du langage
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Sources du coeur (tout sauf main.cpp et bindings.cpp)
file(GLOB SOURCES "*.cpp")
list(REMOVE_ITEM SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/bindings.cpp"
)

# Executable en ligne de commande
add_executable(${PROJECT_NAME} ${SOURCES} main.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python via pybind11 (tous les .cpp sauf main.cpp)
find_package(pybind11 REQUIRED)
pybind11_add_module(bibliotheque_py ${SOURCES} bindings.cpp)
target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
