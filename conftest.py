import sys
import os

# Add src directory to sys.path so that imports from src work in tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
