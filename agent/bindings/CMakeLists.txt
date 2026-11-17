# Module Python construit avec pybind11.
# Les sources metier sont recompilee ici : le code C++ existant n'est pas modifie.
pybind11_add_module(bibliotheque_py
    bindings.cpp
    ${PROJECT_SOURCE_DIR}/book.cpp
    ${PROJECT_SOURCE_DIR}/library.cpp
    ${PROJECT_SOURCE_DIR}/user.cpp
    ${PROJECT_SOURCE_DIR}/filemanager.cpp
)

target_include_directories(bibliotheque_py PRIVATE ${PROJECT_SOURCE_DIR})

set_target_properties(bibliotheque_py PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    # Sortie previsible pour PYTHONPATH=agent/build/python
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/python
)

target_compile_options(bibliotheque_py PRIVATE -Wall -Wextra -Wpedantic)
