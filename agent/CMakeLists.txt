cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

set(CORE_SOURCES
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

add_library(bibliotheque_core STATIC ${CORE_SOURCES})
set_target_properties(bibliotheque_core PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    POSITION_INDEPENDENT_CODE ON
)
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE bibliotheque_core)

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bindings.cpp")
    pybind11_add_module(bibliotheque_py bindings.cpp)
    target_link_libraries(bibliotheque_py PRIVATE bibliotheque_core)
    set_target_properties(bibliotheque_py PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
    )
    target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
endif()
