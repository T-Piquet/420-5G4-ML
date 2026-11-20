@echo off
setlocal
pushd "%~dp0.."

echo === Preparation de l'environnement Windows ===
python -m pip install pybind11
if errorlevel 1 goto :error

for /f "delims=" %%P in ('python -m pybind11 --cmakedir') do set "PYBIND11_DIR=%%P"
for /f "delims=" %%E in ('python -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%E"
for /f "delims=" %%A in ('python -c "import struct; print('x64' if struct.calcsize('P') == 8 else 'Win32')"') do set "ARCH=%%A"

echo Python   : %PYTHON_EXE% (%ARCH%)
echo pybind11 : %PYBIND11_DIR%

echo.
echo === Compilation (MSVC, configuration Release) ===
cmake -S . -B build -G "Visual Studio 17 2022" -A %ARCH% -Dpybind11_DIR="%PYBIND11_DIR%" -DPython3_EXECUTABLE="%PYTHON_EXE%"
if errorlevel 1 goto :error

cmake --build build --config Release
if errorlevel 1 goto :error

echo.
echo === Verification ===
python python\gui.py --selftest
if errorlevel 1 goto :error

echo.
echo Termine. Le module se trouve dans python\bibliotheque_py*.pyd.
echo Lancez python\gui.py ou double-cliquez sur python\lancer_gui.bat.
popd
pause
exit /b 0

:error
echo.
echo Echec. Verifiez : Python python.org avec tkinter, Visual Studio Build Tools
echo (developpement desktop avec C++), CMake >= 3.21 et pybind11 installe via pip.
popd
pause
exit /b 1
