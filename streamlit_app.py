# Streamlit Cloud entry point
# This file imports and runs the main application

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
