cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

add_library(bibliotheque_core STATIC library.cpp book.cpp user.cpp filemanager.cpp activitylog.cpp)
set_target_properties(bibliotheque_core PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_compile_features(bibliotheque_core PUBLIC cxx_std_17)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE bibliotheque_core)

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} bibliotheque_core PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)

option(BIBLIOTHEQUE_BUILD_PYTHON "Construire le module Python" OFF)
if(BIBLIOTHEQUE_BUILD_PYTHON)
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)
    pybind11_add_module(_bibliotheque bindings.cpp)
    target_link_libraries(_bibliotheque PRIVATE bibliotheque_core)
    set_target_properties(_bibliotheque PROPERTIES CXX_EXTENSIONS OFF)
endif()
