from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

extensions = [
    Pybind11Extension(
        "bibliotheque",
        [
            "python_bindings.cpp",
            "../book.cpp",
            "../library.cpp",
            "../user.cpp",
            "../filemanager.cpp",
        ],
        include_dirs=[".."],
        cxx_std=17,
    ),
]

setup(
    name="bibliotheque",
    version="0.1.0",
    description="C++ Library System Python bindings using pybind11",
    ext_modules=extensions,
    cmdclass={"build_ext": build_ext},
    python_requires=">=3.8",
)
