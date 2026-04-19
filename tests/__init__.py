# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

