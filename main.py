#!/usr/bin/env python3
"""
ChordMaster — Aplicação Desktop Interativa de Teoria Musical e Prática de Exercícios.
Ponto de entrada principal da aplicação.
"""
import os
import sys
import tkinter

# Check if running under outdated Tk 8.5 (Apple macOS system python)
# If .venv exists with modern Tk 9.0/8.6, auto-re-exec into the virtual environment
if tkinter.TkVersion < 8.6:
    venv_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python3")
    if os.path.exists(venv_py) and os.path.realpath(sys.executable) != os.path.realpath(venv_py):
        os.execv(venv_py, [venv_py] + sys.argv)

import customtkinter as ctk
from gui.app import ChordMasterApp

# Pre-initialize CustomTkinter appearance settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def main():
    """Inicializa e executa a aplicação ChordMaster."""
    try:
        app = ChordMasterApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
