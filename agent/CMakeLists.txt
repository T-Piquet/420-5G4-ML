cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

# Sources communes au programme C++ et au module Python
set(CORE_SOURCES
    book.cpp
    user.cpp
    library.cpp
    filemanager.cpp
)

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

# Module Python (pybind11) utilise par l'interface graphique ui.py
find_package(pybind11 CONFIG QUIET)
if(pybind11_FOUND)
    pybind11_add_module(bibliotheque_core bindings/bindings.cpp ${CORE_SOURCES})
    target_include_directories(bibliotheque_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
    set_target_properties(bibliotheque_core PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    )
else()
    message(WARNING "pybind11 introuvable : le module Python bibliotheque_core ne sera pas construit.")
endif()
