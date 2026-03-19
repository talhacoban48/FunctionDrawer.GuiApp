@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Function Drawer - Build

echo ============================================
echo   Function Drawer - PyInstaller Build
echo ============================================
echo.

:: PyInstaller kurulu mu?
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] PyInstaller bulunamadi.
    echo        Kurmak icin: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

:: Eski build temizle
if exist "dist\FunctionDrawer" (
    echo [1/3] Eski build temizleniyor...
    rmdir /s /q "dist\FunctionDrawer"
)
if exist "build" (
    rmdir /s /q "build"
)

echo [2/3] Derleniyor...
echo.

pyinstaller ^
    --noconfirm ^
    --windowed ^
    --name "FunctionDrawer" ^
    --icon "assets\favicon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "matplotlib.backends.backend_qt5agg" ^
    --hidden-import "sympy.parsing.sympy_parser" ^
    --hidden-import "sympy.utilities.lambdify" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Derleme basarisiz!
    pause
    exit /b 1
)

echo.
echo [3/3] Tamamlandi!
echo.
echo Cikti: dist\FunctionDrawer\FunctionDrawer.exe
echo.
echo Installer olusturmak icin installer.iss dosyasini
echo Inno Setup ile acip derleyin.
echo.
pause
