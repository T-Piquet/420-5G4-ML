#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_core, m) {
    m.doc() = "Liaison pybind11 du moteur C++ de la bibliothèque";
    m.attr("__version__") = "0.1.0";
}
