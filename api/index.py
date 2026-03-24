import sys
import os

# Agregar el directorio raíz del proyecto al path
# para que Vercel pueda resolver los imports de main, routers, etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
