@echo off
echo Building PDF to Markdown Converter executable...

REM Make sure you're in the correct conda environment with PyInstaller installed
REM conda activate your_pyinstaller_env

REM PyInstaller command for PDF to Markdown Converter
pyinstaller --name PDF2MarkdownConverter ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --hidden-import pymupdf4llm ^
    --hidden-import pymupdf ^
    --hidden-import fitz ^
    --hidden-import frontend ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.ttk ^
    --hidden-import threading ^
    --hidden-import pathlib ^
    --hidden-import typing ^
    --hidden-import re ^
    --collect-all pymupdf4llm ^
    --collect-all pymupdf ^
    pdf_to_markdown_gui.py

echo.
echo Build complete! Check the 'dist' folder for PDF2MarkdownConverter.exe
pause
