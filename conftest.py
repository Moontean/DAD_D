# Ensure project root is on sys.path so `from <service>.main import ...` works
import os
import sys
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
