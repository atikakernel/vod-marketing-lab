# tests/conftest.py
import sys, os

# Inserta la carpeta raíz del proyecto en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
