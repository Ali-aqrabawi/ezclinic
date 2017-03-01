import os
import sys

def fix_path():
    lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "lib")

    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

    try:
        import wrapper_util
    except ImportError:
        appengine_path = os.path.join(lib_path, "google_appengine")
        sys.path.insert(0, appengine_path)
