# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import os
import sys

SRC = os.path.join(os.path.dirname(__file__), "src")
if os.path.isdir(SRC) and SRC not in sys.path:
    sys.path.insert(0, SRC)
