cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

file(GLOB SOURCES "*.cpp")
add_executable(${PROJECT_NAME} ${SOURCES})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python (interface graphique customtkinter) via pybind11.
# Mettre -DBUILD_PYTHON_BINDINGS=OFF pour ne compiler que le programme console.
option(BUILD_PYTHON_BINDINGS "Construire le module Python bibliotheque_py" ON)
if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 CONFIG REQUIRED)
    add_subdirectory(bindings)
endif()
