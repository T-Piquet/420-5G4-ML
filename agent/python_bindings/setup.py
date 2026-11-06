from setuptools import setup, Extension
import sys
from pybind11.setup_helpers import Pybind11Extension, build_ext

extensions = [
    Pybind11Extension(
        "bibliotheque",
        ["python_bindings.cpp", "book.cpp", "library.cpp", "user.cpp", "filemanager.cpp"],
        include_dirs=["../include/", "."],
    ),
]

class GetPybind11Cmd(build_ext):
    def run(self):
        import os
        import subprocess
        pybind_src = os.path.join(os.path.dirname(__file__), '..', 'python_bindings', '..', 'build', 'cmake-build-release', 'lib', 'pybind11')
        
        if not os.path.exists(python_bindings.src):
            raise RuntimeError("pybind11 source required at: " + pybind_src)
        
        self.inplace = True
        super().run()

if hasattr(sys, 'version_info') and sys.version_info >= (3, 8):
    setup(
        name="bibliotheque",
        version="0.1.0",
        description="C++ Library System Python bindings using pybind11",
        ext_modules=extensions,
        cmdclass={"build_ext": GetPybind11Cmd},
        python_requires=">=3.8",
    )
